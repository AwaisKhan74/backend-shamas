from django.contrib import admin
from .models import LeaveRequest, Penalty, DailySummary


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['requester', 'start_date', 'end_date', 'status', 'approved_by', 'created_at']
    list_filter = ['status', 'start_date', 'created_at']
    search_fields = ['requester__work_id', 'reason']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    list_display = ['user', 'store', 'penalty_type', 'amount', 'points_deducted', 'status', 'issued_by', 'issued_at']
    list_filter = ['penalty_type', 'status', 'issued_at']
    search_fields = ['user__work_id', 'store__name', 'reason']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'issued_at'


@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = ['counter', 'date', 'total_visits', 'successful_visits', 'skipped_visits', 'revenue_generated']
    list_filter = ['date', 'created_at']
    search_fields = ['counter__work_id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
