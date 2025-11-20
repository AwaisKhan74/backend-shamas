from django.contrib import admin

from .models import LeaveRequest


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = [
        "requested_by",
        "leave_type",
        "start_date",
        "end_date",
        "status",
        "approver",
        "reviewed_at",
        "created_at",
    ]
    list_filter = ["status", "leave_type", "start_date", "approver"]
    search_fields = ["requested_by__work_id", "requested_by__email", "description", "reviewer_note"]
    readonly_fields = ["created_at", "updated_at", "reviewed_at"]

