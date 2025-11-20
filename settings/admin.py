from django.contrib import admin
from .models import (
    SystemSetting, ProfileSetting, CounterSetting,
    LeaveSetting, ReportSetting, SupportTicket, QualityCheck
)


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'data_type', 'updated_by', 'updated_at']
    list_filter = ['data_type', 'updated_at']
    search_fields = ['key', 'description']
    readonly_fields = ['updated_at']


@admin.register(ProfileSetting)
class ProfileSettingAdmin(admin.ModelAdmin):
    list_display = ['user', 'theme_preference', 'created_at', 'updated_at']
    search_fields = ['user__work_id', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CounterSetting)
class CounterSettingAdmin(admin.ModelAdmin):
    list_display = ['counter', 'setting_key', 'setting_value', 'updated_at']
    list_filter = ['setting_key', 'updated_at']
    search_fields = ['counter__employee_id', 'setting_key']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LeaveSetting)
class LeaveSettingAdmin(admin.ModelAdmin):
    list_display = ['max_leaves_per_year', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ReportSetting)
class ReportSettingAdmin(admin.ModelAdmin):
    list_display = ['report_type', 'updated_at']
    search_fields = ['report_type']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['subject', 'user', 'status', 'priority', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['subject', 'user__work_id', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(QualityCheck)
class QualityCheckAdmin(admin.ModelAdmin):
    list_display = ['checked_by', 'related_entity_type', 'related_entity_id', 'status', 'created_at']
    list_filter = ['status', 'related_entity_type', 'created_at']
    search_fields = ['checked_by__work_id', 'comments']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
