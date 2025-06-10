# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Customize the add and change forms if needed
    # You might want to create custom forms in users/forms.py for this
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'bio', 'profile_picture', 'phone_number', 'country')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type', 'bio', 'profile_picture', 'phone_number', 'country')}),
    )
    list_display = ['username', 'email', 'user_type', 'is_staff', 'is_active']
    list_filter = ['user_type', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'phone_number']

admin.site.register(CustomUser, CustomUserAdmin)