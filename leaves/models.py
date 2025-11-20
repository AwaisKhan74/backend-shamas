from django.conf import settings
from django.db import models
from django.utils import timezone


class LeaveRequest(models.Model):
    """
    Represents an employee leave request with optional supporting document.
    """

    class LeaveType(models.TextChoices):
        SICK = "SICK", "Sick Leave"
        CASUAL = "CASUAL", "Causal Leave"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leave_requests_submitted",
        help_text="User who submitted the leave request.",
    )
    leave_type = models.CharField(
        max_length=20,
        choices=LeaveType.choices,
        default=LeaveType.SICK,
        db_index=True,
    )
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)
    document = models.ForeignKey(
        "core.FileManager",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="leave_requests",
        help_text="Optional supporting document stored in File Manager.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="leave_requests_reviewed",
        help_text="Manager or admin who reviewed the request.",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewer_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "leaves_leave_requests"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["requested_by", "start_date", "end_date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.get_leave_type_display()} ({self.start_date} - {self.end_date})"

    def mark_reviewed(self, status, reviewer, note=""):
        self.status = status
        self.approver = reviewer
        self.reviewed_at = timezone.now()
        if note:
            self.reviewer_note = note
        self.save(update_fields=["status", "approver", "reviewed_at", "reviewer_note", "updated_at"])

