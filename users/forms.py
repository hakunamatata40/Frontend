# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    # Add user_type field to registration form
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES, initial="student")
    email = forms.EmailField(required=True) # Ensure email is required

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'user_type',)

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields # You can add custom fields here if you want to allow admin to change them