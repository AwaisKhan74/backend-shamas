from django.db import models
from django.core.validators import MinValueValidator
from users.models import User
from core.models import Counter, Route, Store


class LeaveRequest(models.Model):
    """
    Leave request model for managing leave requests from field agents.
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='leave_requests',
        limit_choices_to={'role': 'FIELD_AGENT'}
    )
    
    request_date = models.DateField()
    start_date = models.DateField()
    end_date = models.DateField()
    
    reason = models.TextField()
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True
    )
    
    # Approval
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves',
        limit_choices_to={'role': 'MANAGER'}
    )
    
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leave_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['requester', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"Leave Request: {self.requester.work_id} - {self.start_date} to {self.end_date}"
    
    @property
    def duration_days(self):
        """Calculate leave duration in days."""
        return (self.end_date - self.start_date).days + 1


class Penalty(models.Model):
    """
    Penalty model for tracking penalties issued to field agents.
    """
    
    PENALTY_TYPE_CHOICES = [
        ('FINANCIAL', 'Financial'),
        ('WARNING', 'Warning'),
    ]
    
    STATUS_CHOICES = [
        ('ISSUED', 'Issued'),
        ('PAID', 'Paid'),
        ('DISPUTED', 'Disputed'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='penalties_received',
        limit_choices_to={'role': 'FIELD_AGENT'}
    )
    
    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='penalties'
    )
    
    store = models.ForeignKey(
        Store,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='penalties'
    )
    
    reason = models.TextField(
        help_text="Reason for penalty (e.g., 'store skipped', 'route incomplete')"
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Financial penalty amount if applicable"
    )
    
    points_deducted = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Points deducted for this penalty"
    )
    
    store_visit = models.ForeignKey(
        'operations.StoreVisit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='penalties',
        help_text="Store visit that resulted in this penalty"
    )
    
    penalty_type = models.CharField(
        max_length=20,
        choices=PENALTY_TYPE_CHOICES,
        default='WARNING'
    )
    
    issued_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='penalties_assigned',
        limit_choices_to={'role': 'MANAGER'}
    )
    
    issued_at = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ISSUED',
        db_index=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'penalties'
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['penalty_type']),
            models.Index(fields=['issued_at']),
        ]
    
    def __str__(self):
        return f"Penalty: {self.user.work_id} - {self.penalty_type} - {self.amount or 'N/A'}"


class DailySummary(models.Model):
    """
    Daily summary model for tracking daily performance of counters/field agents.
    """
    
    counter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='daily_summaries',
        limit_choices_to={'role': 'FIELD_AGENT'}
    )
    
    date = models.DateField(db_index=True)
    
    total_visits = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    successful_visits = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    skipped_visits = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    revenue_generated = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    other_metrics = models.JSONField(
        null=True,
        blank=True,
        help_text="Flexible storage for additional metrics"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daily_summaries'
        ordering = ['-date']
        unique_together = [['counter', 'date']]
        indexes = [
            models.Index(fields=['counter', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"Daily Summary: {self.counter.work_id} - {self.date}"
    
    @property
    def completion_rate(self):
        """Calculate completion rate as percentage."""
        if self.total_visits > 0:
            return (self.successful_visits / self.total_visits) * 100
        return 0
