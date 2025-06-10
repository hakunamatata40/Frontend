# courses/admin.py
from django.contrib import admin
from django.apps import apps
from django.contrib.contenttypes.admin import GenericStackedInline # For Content-Type
from .models import Subject, Course, Module, Content, TextContent, VideoContent, ImageContent, FileContent, Enrollment
from users.models import CustomUser # Import CustomUser for filtering

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

# Inlines for Content-Type Framework
class ContentInline(GenericStackedInline):
    model = Content
    ct_field = 'content_type'
    ct_fk_field = 'object_id'
    extra = 0
    # You might need to list available content types here
    # E.g., 'textcontent', 'videocontent' etc.

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title']
    inlines = [ContentInline] # This will allow adding generic content to modules
    ordering = ['order']

class ModuleInline(admin.StackedInline):
    model = Module
    extra = 0 # No empty forms by default
    show_change_link = True # Allow editing existing modules from course admin
    ordering = ['order']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'instructor', 'price', 'is_published', 'created']
    list_filter = ['is_published', 'created', 'subject']
    search_fields = ['title', 'overview', 'instructor__username']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]
    raw_id_fields = ('instructor',) # Better for many instructors

    # Restrict instructor dropdown to users with user_type='instructor'
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "instructor":
            kwargs["queryset"] = CustomUser.objects.filter(user_type='instructor')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Register individual content types for direct access if needed
admin.site.register(TextContent)
admin.site.register(VideoContent)
admin.site.register(ImageContent)
admin.site.register(FileContent)
admin.site.register(Enrollment)