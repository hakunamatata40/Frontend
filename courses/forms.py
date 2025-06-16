# courses/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Course, Module, Content, TextContent, VideoContent, ImageContent, FileContent, Subject
from taggit.forms import TagWidget # Import TagWidget for better tag display/input

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        # ADDED 'image' to the fields list
        fields = ['subject', 'title', 'slug', 'overview', 'price', 'is_published', 'tags', 'image']
        widgets = {
            'overview': forms.Textarea(attrs={'rows': 5, 'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500'}),
            'slug': forms.TextInput(attrs={'placeholder': 'Auto-generated if left blank', 'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500'}),
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500'}),
            'price': forms.NumberInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-purple-600'}),
            # Using TagWidget for tags for better visual and functionality if you're using django-taggit's default JS
            'tags': TagWidget(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500', 'placeholder': 'Enter tags separated by commas'}),
            # NEW: Widget for the image field to give it a file input look
            'image': forms.ClearableFileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure 'tags' field is handled correctly by django-taggit
        self.fields['tags'].required = False # Make tags optional

        # Apply common styling to fields that don't have specific widgets yet
        # This is a more robust way to apply classes to all text/number/select inputs
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.Textarea, forms.Select)):
                if 'class' in field.widget.attrs:
                    field.widget.attrs['class'] += ' w-full p-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500'
                else:
                    field.widget.attrs['class'] = 'w-full p-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500'
            # Specific styling for the subject dropdown
            if field_name == 'subject':
                field.widget.attrs.update({'class': 'block appearance-none w-full bg-white border border-gray-300 text-gray-700 py-2 px-3 pr-8 rounded-md leading-tight focus:outline-none focus:bg-white focus:border-purple-500'})


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500'}),
            'order': forms.NumberInput(attrs={'min': 0, 'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500'}),
        }

    def clean_order(self):
        order = self.cleaned_data.get('order')
        if order is None:
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
            'content': forms.Textarea(attrs={'rows': 10, 'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500'}),
        }

class VideoContentForm(forms.ModelForm):
    class Meta:
        model = VideoContent
        fields = ['video_url']
        widgets = {
            'video_url': forms.URLInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500', 'placeholder': 'Paste YouTube, Vimeo, or direct video URL'}),
        }

class ImageContentForm(forms.ModelForm):
    class Meta:
        model = ImageContent
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'}),
        }

class FileContentForm(forms.ModelForm):
    class Meta:
        model = FileContent
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100'}),
        }


class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500'}),
            'order': forms.NumberInput(attrs={'min': 0, 'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500'}),
        }