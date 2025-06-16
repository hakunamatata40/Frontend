# courses/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Count, Q
import django.db.models as models
import json

from .models import Course, Subject, Module, Content, TextContent, VideoContent, ImageContent, FileContent, Enrollment
from users.models import CustomUser
from .forms import CourseForm, ModuleForm, TextContentForm, VideoContentForm, ImageContentForm, FileContentForm, ContentForm
from django.forms.models import model_to_dict
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse, Http404


# Mixins for permissions
class InstructorRequiredMixin(UserPassesTestMixin):
    """
    Mixin to ensure the user is an instructor.
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'instructor'

class CourseOwnerRequiredMixin(UserPassesTestMixin):
    """
    Mixin to ensure the user is the instructor of the course.
    """
    def test_func(self):
        course_id = self.kwargs.get('pk') or self.kwargs.get('course_id')
        if not course_id:
            return False
        try:
            course = Course.objects.get(id=course_id)
            return course.instructor == self.request.user
        except Course.DoesNotExist:
            return False

# --- Public Course Views ---
class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 10

    def get_queryset(self):
        # Only show published courses
        queryset = super().get_queryset().filter(is_published=True)

        # Filter by subject
        subject_slug = self.kwargs.get('subject_slug')
        if subject_slug:
            subject = get_object_or_404(Subject, slug=subject_slug)
            queryset = queryset.filter(subject=subject)

        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(overview__icontains=query) |
                Q(instructor__username__icontains=query) |
                Q(tags__name__icontains=query) # Search by tags
            ).distinct()

        return queryset.annotate(num_modules=Count('modules')).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subjects'] = Subject.objects.annotate(total_courses=Count('courses', filter=Q(courses__is_published=True)))
        context['current_subject_slug'] = self.kwargs.get('subject_slug')
        context['query'] = self.request.GET.get('q', '')
        return context


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_queryset(self):
        # Only allow access to published courses unless the user is the instructor
        queryset = super().get_queryset()
        if self.request.user.is_authenticated and self.request.user.user_type == 'instructor':
            # Instructors can see their unpublished courses
            return queryset
        return queryset.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        user_is_enrolled = False
        enrollment = None

        if self.request.user.is_authenticated:
            # Check if the user is an instructor and the owner of the course
            # Instructors of their own courses also implicitly "have access" to the chat
            if self.request.user.user_type == 'instructor' and course.instructor == self.request.user:
                # We'll use 'user_is_enrolled' to mean 'has access to chat/course content' for templates
                user_is_enrolled = True 
                # For instructors, 'enrollment' object doesn't apply directly,
                # but if your system requires it for some reason, you might create a dummy
                # or special enrollment record for them, or just rely on `user_is_enrolled` being True.
                # For now, we'll keep it None as they are not "enrolled" in the student sense.
            elif self.request.user.user_type == 'student':
                # For students, check for actual enrollment
                try:
                    enrollment = Enrollment.objects.get(student=self.request.user, course=course)
                    user_is_enrolled = True
                except Enrollment.DoesNotExist:
                    user_is_enrolled = False

        context['user_is_enrolled'] = user_is_enrolled
        context['enrollment'] = enrollment
        return context

# --- Instructor Dashboard & Course Management ---
class InstructorDashboardView(LoginRequiredMixin, InstructorRequiredMixin, ListView):
    model = Course
    template_name = 'courses/instructor_dashboard.html'
    context_object_name = 'courses'
    paginate_by = 10

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user).annotate(num_modules=Count('modules'))

class CourseCreateView(LoginRequiredMixin, InstructorRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('instructor_dashboard')

    def form_valid(self, form):
        form.instance.instructor = self.request.user # Assign the current instructor
        messages.success(self.request, "Course created successfully!")
        return super().form_valid(form)

class CourseUpdateView(LoginRequiredMixin, InstructorRequiredMixin, CourseOwnerRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'

    def get_success_url(self):
        messages.success(self.request, "Course updated successfully!")
        return reverse_lazy('course_detail', args=[self.object.id, self.object.slug])

class CourseDeleteView(LoginRequiredMixin, InstructorRequiredMixin, CourseOwnerRequiredMixin, DeleteView):
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('instructor_dashboard')

    def form_valid(self, form):
        messages.success(self.request, "Course deleted successfully!")
        return super().form_valid(form)


# Module Management
class ModuleCreateUpdateView(LoginRequiredMixin, InstructorRequiredMixin, CourseOwnerRequiredMixin, View):
    template_name = 'courses/module_form.html'
    module_form = ModuleForm

    def get_object(self):
        # Get module if updating, otherwise None
        module_id = self.kwargs.get('pk')
        return get_object_or_404(Module, pk=module_id, course_id=self.kwargs['course_id']) if module_id else None

    def get(self, request, course_id, pk=None):
        course = get_object_or_404(Course, id=course_id, instructor=request.user)
        module = self.get_object()
        form = self.module_form(instance=module)
        return render(request, self.template_name, {'form': form, 'course': course, 'module': module})

    def post(self, request, course_id, pk=None):
        course = get_object_or_404(Course, id=course_id, instructor=request.user)
        module = self.get_object()
        form = self.module_form(request.POST, instance=module)

        if form.is_valid():
            new_module = form.save(commit=False)
            new_module.course = course
            # Auto-assign order if not provided
            if new_module.order is None:
                max_order = course.modules.aggregate(models.Max('order'))['max_order']
                new_module.order = (max_order or 0) + 1
            new_module.save()
            messages.success(request, "Module saved successfully!")
            return redirect('course_detail', pk=course.id, slug=course.slug)
        return render(request, self.template_name, {'form': form, 'course': course, 'module': module})

class ModuleDeleteView(LoginRequiredMixin, InstructorRequiredMixin, CourseOwnerRequiredMixin, DeleteView):
    model = Module
    template_name = 'courses/module_confirm_delete.html'

    def get_success_url(self):
        module = self.get_object()
        messages.success(self.request, "Module deleted successfully!")
        return reverse_lazy('course_detail', args=[module.course.id, module.course.slug])


# Content Management (Generalized View)
class ContentCreateUpdateView(LoginRequiredMixin, InstructorRequiredMixin, View):
    template_name = 'courses/content_form.html'

    def get_content_model(self, model_name):
        try:
            return apps.get_model('courses', model_name.capitalize())
        except LookupError:
            raise Http404(f"Content type '{model_name}' not found.")

    def get_content_form(self, model_name, *args, **kwargs):
        content_model = self.get_content_model(model_name)
        if content_model == TextContent:
            return TextContentForm(*args, **kwargs)
        elif content_model == VideoContent:
            return VideoContentForm(*args, **kwargs)
        elif content_model == ImageContent:
            return ImageContentForm(*args, **kwargs)
        elif content_model == FileContent:
            return FileContentForm(*args, **kwargs)
        return None # Should not happen if model_name is valid

    def get_object(self, content_id):
        return get_object_or_404(Content, id=content_id)

    def get(self, request, module_id, model_name, pk=None): # pk is for content_id
        module = get_object_or_404(Module, id=module_id, course__instructor=request.user)
        content_item = None
        form = None
        content_obj = None

        if pk: # If updating existing content
            content_obj = self.get_object(pk)
            # Ensure the content belongs to the correct module and instructor
            if content_obj.module != module:
                raise Http404("Content does not belong to this module.")
            content_item = content_obj.item # Get the actual TextContent, VideoContent etc. object
            form = self.get_content_form(model_name, instance=content_item)
            content_meta_form = ContentForm(instance=content_obj) # Form for general Content model fields
        else: # If creating new content
            form = self.get_content_form(model_name)
            content_meta_form = ContentForm()

        if form is None:
            raise Http404(f"Invalid content type: {model_name}")

        context = {
            'module': module,
            'form': form,
            'content_meta_form': content_meta_form,
            'model_name': model_name,
            'content_obj': content_obj, # The Content instance
        }
        return render(request, self.template_name, context)

    def post(self, request, module_id, model_name, pk=None):
        module = get_object_or_404(Module, id=module_id, course__instructor=request.user)
        content_item = None
        content_obj = None

        if pk: # Update existing content
            content_obj = self.get_object(pk)
            if content_obj.module != module:
                raise Http404("Content does not belong to this module.")
            content_item = content_obj.item # Get the actual TextContent, VideoContent etc. object
            form = self.get_content_form(model_name, request.POST, request.FILES, instance=content_item)
            content_meta_form = ContentForm(request.POST, instance=content_obj)
        else: # Create new content
            form = self.get_content_form(model_name, request.POST, request.FILES)
            content_meta_form = ContentForm(request.POST)

        if form is None:
            raise Http404(f"Invalid content type: {model_name}")

        if form.is_valid() and content_meta_form.is_valid():
            content_item_instance = form.save() # Saves TextContent, VideoContent etc.

            if not pk: # If creating new Content object (only on first creation)
                content_type = ContentType.objects.get_for_model(content_item_instance)
                content_obj = Content(
                    module=module,
                    content_type=content_type,
                    object_id=content_item_instance.id,
                    title=content_meta_form.cleaned_data['title'],
                    order=content_meta_form.cleaned_data['order']
                )
                # Auto-assign order if not provided
                if content_obj.order is None:
                    max_order = module.contents.aggregate(models.Max('order'))['max_order']
                    content_obj.order = (max_order or 0) + 1
                content_obj.save()
            else: # If updating existing Content object (only on update)
                content_obj.title = content_meta_form.cleaned_data['title']
                content_obj.order = content_meta_form.cleaned_data['order']
                content_obj.save()

            messages.success(request, f"{model_name.capitalize()} content saved successfully!")
            return redirect('course_detail', pk=module.course.id, slug=module.course.slug)

        context = {
            'module': module,
            'form': form,
            'content_meta_form': content_meta_form,
            'model_name': model_name,
            'content_obj': content_obj,
        }
        return render(request, self.template_name, context)

class ContentDeleteView(LoginRequiredMixin, InstructorRequiredMixin, DeleteView):
    model = Content
    template_name = 'courses/content_confirm_delete.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Ensure the content belongs to the current instructor's course
        if obj.module.course.instructor != self.request.user:
            raise Http404("You are not authorized to delete this content.")
        return obj

    def get_success_url(self):
        content = self.get_object()
        messages.success(self.request, "Content deleted successfully!")
        return reverse_lazy('course_detail', args=[content.module.course.id, content.module.course.slug])


# --- Student Views ---
def enroll_course(request, course_id): # Decorator @LoginRequiredMixin needs to be above the function
    course = get_object_or_404(Course, id=course_id)
    if request.user.user_type != 'student':
        messages.error(request, "Only students can enroll in courses.")
        return redirect('course_detail', pk=course.id, slug=course.slug)

    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.info(request, "You are already enrolled in this course.")
        return redirect('course_detail', pk=course.id, slug=course.slug)

    if course.price == 0.00:
        # Free course enrollment
        Enrollment.objects.create(student=request.user, course=course)
        messages.success(request, f"You have successfully enrolled in the free course: {course.title}!")
        return redirect('my_courses')
    else:
        # Paid course - redirect to checkout
        messages.info(request, "Redirecting to checkout for payment.")
        return redirect('checkout', course_id=course.id)

class EnrolledCourseListView(LoginRequiredMixin, ListView):
    model = Enrollment
    template_name = 'courses/my_courses.html'
    context_object_name = 'enrollments'

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user).select_related('course').order_by('-enrolled_at')

class CoursePlayerView(LoginRequiredMixin, DetailView):
    model = Enrollment
    template_name = 'courses/course_player.html'
    context_object_name = 'enrollment'
    slug_field = 'pk' # We're using enrollment_id as pk for lookup

    def get_object(self, queryset=None):
        enrollment_id = self.kwargs.get('enrollment_id')
        enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=self.request.user)
        return enrollment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrollment = self.get_object()
        course = enrollment.course

        # Ensure module_id and content_id are valid for this enrollment and course
        module_id = self.kwargs.get('module_id')
        content_id = self.kwargs.get('content_id')

        selected_module = None
        selected_content = None

        if module_id:
            try:
                selected_module = course.modules.get(id=module_id)
            except Module.DoesNotExist:
                raise Http404("Module not found in this course.")

        # If no module_id or content_id, try to get the first content
        if not selected_module and course.modules.exists():
            selected_module = course.modules.first()
            if selected_module.contents.exists():
                selected_content = selected_module.contents.first()
        elif selected_module and not content_id and selected_module.contents.exists():
            selected_content = selected_module.contents.first()
        elif selected_module and content_id:
            try:
                selected_content = selected_module.contents.get(id=content_id)
            except Content.DoesNotExist:
                raise Http404("Content not found in this module.")

        context['course'] = course
        context['selected_module'] = selected_module
        context['selected_content'] = selected_content
        context['modules'] = course.modules.prefetch_related('contents') # Eager load contents

        # Calculate progress for display
        total_contents_in_course = course.modules.aggregate(total=Count('contents'))['total']
        context['total_contents_in_course'] = total_contents_in_course

        # Mark content as completed when accessed
        if selected_content and not enrollment.completed_contents.filter(id=selected_content.id).exists():
            enrollment.completed_contents.add(selected_content)
            messages.success(self.request, f"Marked '{selected_content.title or selected_content.item.__class__.__name__}' as completed!")

        context['completed_content_ids'] = list(enrollment.completed_contents.values_list('id', flat=True))
        context['progress_percentage'] = enrollment.get_progress()

        return context

# API endpoint for updating content order (requires JavaScript for drag-and-drop)
class ContentOrderView(LoginRequiredMixin, InstructorRequiredMixin, View):
    def post(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__instructor=request.user)

        data = request.body.decode('utf-8')
        try:
            content_order = json.loads(data) # Expects a list of {id: content_id, order: new_order}
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        for item in content_order:
            try:
                content_obj = Content.objects.get(id=item['id'], module=module)
                content_obj.order = item['order']
                content_obj.save()
            except Content.DoesNotExist:
                return JsonResponse({'error': f"Content with ID {item['id']} not found or not in module"}, status=404)
            except KeyError:
                return JsonResponse({'error': 'Missing ID or order in payload'}, status=400)

        return JsonResponse({'message': 'Content order updated successfully'})