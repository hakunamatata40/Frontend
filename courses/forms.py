# courses/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Course, Module, Content, TextContent, VideoContent, ImageContent, FileContent, Subject

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['subject', 'title', 'slug', 'overview', 'price', 'is_published', 'tags']
        widgets = {
            'overview': forms.Textarea(attrs={'rows': 5}),
            'slug': forms.TextInput(attrs={'placeholder': 'Auto-generated if left blank'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure 'tags' field is handled correctly by django-taggit
        self.fields['tags'].required = False # Make tags optional

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }

    def clean_order(self):
        order = self.cleaned_data.get('order')
        if order is None: # If not provided, it will be handled by save()
            return order
        if order < 0:
            raise forms.ValidationError("Order cannot be negative.")
        return order


# Forms for different content types
class TextContentForm(forms.ModelForm):
    class Meta:
        model = TextContent
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

class VideoContentForm(forms.ModelForm):
    class Meta:
        model = VideoContent
        fields = ['video_url']

class ImageContentForm(forms.ModelForm):
    class Meta:
        model = ImageContent
        fields = ['image']

class FileContentForm(forms.ModelForm):
    class Meta:
        model = FileContent
        fields = ['file']

# Base form for Content model (used with Content-Type Generic relations)
# This isn't directly used for specific content types, but Content formset might be.
class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'order']
        widgets = {
            'order': forms.NumberInput(attrs={'min': 0}),
        }