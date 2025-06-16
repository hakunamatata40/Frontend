# chat/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.utils.decorators import method_decorator
from django.contrib import messages
import json

from .models import ChatRoom, Message
from courses.models import Course, Enrollment

from django.views.generic import ListView

# --- Helper for Authorization (reused by multiple views) ---
def _check_chat_authorization(user, course):
    if not user.is_authenticated:
        return False
    
    is_instructor = (user.user_type == 'instructor' and user == course.instructor)
    is_student_enrolled = (user.user_type == 'student' and
                           Enrollment.objects.filter(student=user, course=course).exists())
    
    return is_instructor or is_student_enrolled

# --- 1. Main Chat Page View (Renders the HTML) ---
class CourseChatView(LoginRequiredMixin, View):
    template_name = 'chat/chat_detail.html'

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        if not _check_chat_authorization(request.user, course):
            messages.error(request, "You are not authorized to access this chat room.")
            return redirect('course_detail', pk=course.id, slug=course.slug) 

        chat_room, created = ChatRoom.objects.get_or_create(course=course)
        
        context = {
            'course': course,
            'chat_room': chat_room,
        }
        return render(request, self.template_name, context)

# --- 2. API View to Fetch Messages (for AJAX Polling) ---
@method_decorator(require_GET, name='dispatch')
class GetChatMessagesView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        if not _check_chat_authorization(request.user, course):
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        chat_room, created = ChatRoom.objects.get_or_create(course=course)
        
        messages = chat_room.messages.order_by('timestamp').values(
            'sender__username', 'content', 'timestamp', 'sender__id'
        )[:50] 
        
        messages_data = [
            {
                'sender_username': msg['sender__username'],
                'content': msg['content'],
                'timestamp': msg['timestamp'].isoformat(),
                'sender_id': msg['sender__id'],
            }
            for msg in messages
        ]
        
        return JsonResponse({'messages': messages_data})

# --- 3. API View to Send Messages (for AJAX POST) ---
@method_decorator(require_POST, name='dispatch')
class PostChatMessageView(LoginRequiredMixin, View):
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        if not _check_chat_authorization(request.user, course):
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        try:
            data = json.loads(request.body)
            message_content = data.get('message')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not message_content or not message_content.strip():
            return JsonResponse({'error': 'Message content cannot be empty'}, status=400)

        chat_room, created = ChatRoom.objects.get_or_create(course=course)
        
        Message.objects.create(
            chat_room=chat_room,
            sender=request.user,
            content=message_content
        )
        
        return JsonResponse({'status': 'Message sent successfully'})

# --- 4. My Chats List View ---
class MyChatsListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'chat/my_chats.html'
    context_object_name = 'chats'

    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'student':
            # FIX: Changed 'enrollment__student' to 'enrollments__student'
            # FIX: Used direct keyword arguments as they are clear and safe
            return Course.objects.filter(enrollments__student=user, chat_room__isnull=False).distinct()
        elif user.user_type == 'instructor':
            # Fix: Ensure consistency with direct keyword arguments
            return Course.objects.filter(instructor=user, chat_room__isnull=False).distinct()
        
        return Course.objects.none()