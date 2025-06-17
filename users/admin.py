from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Fieldsets for editing an existing user
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'bio', 'profile_picture', 'phone_number', 'country', 'pedagogic_level', 'interests')}),
    )
    # Fieldsets for adding a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type', 'bio', 'profile_picture', 'phone_number', 'country', 'pedagogic_level', 'interests')}),
    )

    # Fields to display in the list view of users
    list_display = ['username', 'email', 'user_type', 'pedagogic_level', 'is_staff', 'is_active']
    
    # Fields to use for filtering in the list view
    list_filter = ['user_type', 'pedagogic_level', 'is_staff', 'is_active']
    
    # Fields to search by in the list view
    search_fields = ['username', 'email', 'phone_number', 'country']

    # This is crucial for ManyToManyFields like 'interests' to display as a clean horizontal filter
    filter_horizontal = ('interests',)

admin.site.register(CustomUser, CustomUserAdmin)