from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from courses.models import Subject # Import the Subject model
from django.utils.translation import gettext_lazy as _


class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES, initial="student", label=_("I am a:"))
    email = forms.EmailField(required=True, label=_("Email Address"))
    first_name = forms.CharField(required=True, label=_("First Name"))
    last_name = forms.CharField(required=True, label=_("Last Name"))
    gender = forms.ChoiceField(choices=CustomUser.GENDER_CHOICES, required=False, label=_("Gender"))
    birth_date = forms.DateField(
        required=False,
        label=_("Birth Date"),
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    pedagogic_level = forms.ChoiceField(
        choices=CustomUser.PEDAGOGIC_LEVEL_CHOICES,
        label=_("Your Pedagogic Level"),
        required=True
    )
    interests = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label=_("Your Interests (Select all that apply)"),
        required=False,
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2',
                 'first_name', 'last_name', 'user_type', 'gender', 'birth_date',
                 'pedagogic_level', 'interests', 'bio',
                 'profile_picture', 'phone_number', 'country')

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