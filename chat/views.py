# chat/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.utils.decorators import method_decorator
from django.contrib import messages # For displaying messages to the user
import json # To parse incoming JSON data for messages

# Import models from chat app
from .models import ChatRoom, Message

# Import Course and Enrollment from the courses app for authorization logic
# Make sure these imports match where your Course and Enrollment models are defined
from courses.models import Course, Enrollment

# --- Helper for Authorization (reused by multiple views) ---
def _check_chat_authorization(user, course):
    if not user.is_authenticated:
        return False
    
    # Check if the user is the instructor of the course
    is_instructor = (user.user_type == 'instructor' and user == course.instructor)
    
    # Check if the user is a student enrolled in the course
    is_student_enrolled = (user.user_type == 'student' and
                           Enrollment.objects.filter(student=user, course=course).exists())
    
    return is_instructor or is_student_enrolled

# --- 1. Main Chat Page View (Renders the HTML) ---
class CourseChatView(LoginRequiredMixin, View):
    template_name = 'chat/chat_detail.html'

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        # Authorize access to the chat room
        if not _check_chat_authorization(request.user, course):
            messages.error(request, "You are not authorized to access this chat room.")
            # Redirect to the course detail page or another appropriate page
            return redirect('course_detail', pk=course.id, slug=course.slug) 

        # Get or create the chat room for this course.
        # This ensures a ChatRoom object exists for the course when the page loads.
        chat_room, created = ChatRoom.objects.get_or_create(course=course)
        
        context = {
            'course': course,
            'chat_room': chat_room, # Pass chat_room to template for its ID
        }
        return render(request, self.template_name, context)

# --- 2. API View to Fetch Messages (for AJAX Polling) ---
@method_decorator(require_GET, name='dispatch') # Ensures only GET requests are allowed
class GetChatMessagesView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        # Authorize access to fetch messages
        if not _check_chat_authorization(request.user, course):
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        chat_room, created = ChatRoom.objects.get_or_create(course=course)
        
        # Fetch the latest 50 messages. Adjust count as needed.
        # .values() returns dictionaries, which are easier to JSON serialize.
        messages = chat_room.messages.order_by('timestamp').values(
            'sender__username', 'content', 'timestamp', 'sender__id' # Include sender ID for self-styling
        )[:50] 
        
        # Convert QuerySet to a list of dictionaries for JSON response
        messages_data = [
            {
                'sender_username': msg['sender__username'],
                'content': msg['content'],
                'timestamp': msg['timestamp'].isoformat(), # Format datetime for easy JavaScript parsing
                'sender_id': msg['sender__id'],
            }
            for msg in messages
        ]
        
        return JsonResponse({'messages': messages_data})

# --- 3. API View to Send Messages (for AJAX POST) ---
@method_decorator(require_POST, name='dispatch') # Ensures only POST requests are allowed
class PostChatMessageView(LoginRequiredMixin, View):
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        # Authorize access to send messages
        if not _check_chat_authorization(request.user, course):
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        try:
            # Messages are sent as JSON in the request body
            data = json.loads(request.body)
            message_content = data.get('message')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not message_content or not message_content.strip(): # Check for empty or whitespace-only messages
            return JsonResponse({'error': 'Message content cannot be empty'}, status=400)

        chat_room, created = ChatRoom.objects.get_or_create(course=course)
        
        # Create and save the new message to the database
        Message.objects.create(
            chat_room=chat_room,
            sender=request.user,
            content=message_content
        )
        
        return JsonResponse({'status': 'Message sent successfully'})