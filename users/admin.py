from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model."""
    
    list_display = ['work_id', 'username', 'email', 'role', 'preferred_language', 'is_active', 'date_joined']
    list_filter = ['role', 'preferred_language', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['work_id', 'username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': (
                'work_id', 'role', 'phone_number', 'display_name', 'status',
                'country', 'city', 'address', 'profile_picture',
                'has_gps_permission', 'has_camera_permission',
                'push_notifications_enabled', 'route_reminders_enabled',
                'reward_alerts_enabled', 'qc_alerts_enabled',
                'preferred_language'
            )
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('work_id', 'role', 'email', 'phone_number',
                       'display_name', 'status', 'country', 'city', 'address',
                       'preferred_language')
        }),
    )

    def get_queryset(self, request):
        return User.all_objects.all()

