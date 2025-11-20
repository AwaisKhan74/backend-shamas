from django.contrib import admin
from .models import Break, CheckIn, FlaggedStore, Image, PermissionForm, StoreVisit


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ['user', 'shift_date', 'status', 'timestamp', 'check_out_time', 'total_break_duration', 'created_at']
    list_filter = ['shift_date', 'status', 'timestamp', 'created_at']
    search_fields = ['user__work_id', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'total_break_duration']
    date_hierarchy = 'timestamp'


@admin.register(Break)
class BreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'session', 'route', 'start_time', 'end_time', 'duration', 'created_at']
    list_filter = ['start_time', 'created_at', 'route']
    search_fields = ['user__work_id', 'route__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_time'


@admin.register(StoreVisit)
class StoreVisitAdmin(admin.ModelAdmin):
    list_display = ['user', 'store', 'route', 'status', 'ai_ml_check_status', 'entry_time', 'created_at']
    list_filter = ['status', 'ai_ml_check_status', 'created_at']
    search_fields = ['user__work_id', 'store__name', 'route__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['store_visit', 'user', 'image_type', 'quality_status', 'quality_checked_by', 'captured_at', 'created_at']
    list_filter = ['image_type', 'quality_status', 'captured_at']
    search_fields = ['store_visit__store__name', 'user__work_id']
    readonly_fields = ['created_at', 'quality_checked_at']
    date_hierarchy = 'captured_at'


@admin.register(PermissionForm)
class PermissionFormAdmin(admin.ModelAdmin):
    list_display = [
        'store_visit', 'representative_name', 'representative_designation',
        'permission_received', 'is_flagged', 'submitted_at', 'created_at'
    ]
    list_filter = ['permission_received', 'is_flagged', 'submitted_at', 'created_at']
    search_fields = ['store_visit__store__name', 'representative_name', 'representative_designation']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Store Visit', {
            'fields': ('store_visit',)
        }),
        ('Representative Information', {
            'fields': (
                'representative_name', 'representative_designation', 'representative_contact'
            )
        }),
        ('Permission', {
            'fields': (
                'permission_received', 'signature',
                'permission_granted_confirmed',
                'representative_details_verified',
                'ready_to_begin_collection'
            )
        }),
        ('Status', {
            'fields': ('is_flagged',)
        }),
        ('Additional Data', {
            'fields': ('form_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'created_at', 'updated_at')
        }),
    )
    date_hierarchy = 'submitted_at'


@admin.register(FlaggedStore)
class FlaggedStoreAdmin(admin.ModelAdmin):
    list_display = [
        'store_visit', 'reason', 'flagged_by', 'is_resolved',
        'resolved_by', 'flagged_at', 'created_at'
    ]
    list_filter = ['reason', 'is_resolved', 'flagged_at', 'created_at']
    search_fields = [
        'store_visit__store__name',
        'flagged_by__work_id', 'flagged_by__email',
        'additional_details'
    ]
    readonly_fields = ['flagged_by', 'flagged_at', 'created_at', 'updated_at']
    fieldsets = (
        ('Store Visit', {
            'fields': ('store_visit',)
        }),
        ('Flagging Information', {
            'fields': ('reason', 'additional_details', 'flagged_by', 'flagged_at')
        }),
        ('Resolution', {
            'fields': (
                'is_resolved', 'resolved_by', 'resolved_at', 'resolution_notes'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    date_hierarchy = 'flagged_at'
