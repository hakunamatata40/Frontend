from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from courses.models import Subject # Import the Subject model

class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES, initial="student", label="I am a:")
    email = forms.EmailField(required=True, label="Email Address")

    pedagogic_level = forms.ChoiceField(
        choices=CustomUser.PEDAGOGIC_LEVEL_CHOICES,
        label="Your Pedagogic Level",
        required=True
    )
    interests = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Your Interests (Select all that apply)",
        required=False,
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + (
            'email',
            'user_type',
            'pedagogic_level',
            'interests',
            'bio',
            'profile_picture',
            'phone_number',
            'country',
        )

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        # Instead of concatenating with UserChangeForm.Meta.fields (which is '__all__'),
        # explicitly list all the fields you want to display and edit in the admin.
        # This includes standard AbstractUser fields and your CustomUser fields.
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
            # Add your custom fields from CustomUser here
            'user_type',
            'bio',
            'profile_picture',
            'phone_number',
            'country',
            'pedagogic_level',
            'interests',
        )