from django.db import models
from users.models import User
from core.models import Counter


class SystemSetting(models.Model):
    """
    System-wide configuration settings.
    """
    
    DATA_TYPE_CHOICES = [
        ('STRING', 'String'),
        ('INTEGER', 'Integer'),
        ('BOOLEAN', 'Boolean'),
        ('JSON', 'JSON'),
    ]
    
    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.TextField()
    
    data_type = models.CharField(
        max_length=20,
        choices=DATA_TYPE_CHOICES,
        default='STRING'
    )
    
    description = models.TextField(null=True, blank=True)
    
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'ADMIN'}
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_settings'
        ordering = ['key']
    
    def __str__(self):
        return f"{self.key} = {self.value}"


class ProfileSetting(models.Model):
    """
    User-specific profile settings.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile_settings'
    )
    
    theme_preference = models.CharField(
        max_length=20,
        default='light',
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('auto', 'Auto'),
        ]
    )
    
    notification_settings = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        help_text="Notification preferences as JSON"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'profile_settings'
    
    def __str__(self):
        return f"Profile Settings: {self.user.work_id}"


class CounterSetting(models.Model):
    """
    Counter-specific settings.
    """
    
    counter = models.ForeignKey(
        Counter,
        on_delete=models.CASCADE,
        related_name='counter_settings'
    )
    
    setting_key = models.CharField(max_length=100)
    setting_value = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'counter_settings'
        unique_together = [['counter', 'setting_key']]
        ordering = ['counter', 'setting_key']
    
    def __str__(self):
        return f"{self.counter.employee_id} - {self.setting_key}"


class LeaveSetting(models.Model):
    """
    Leave policy settings.
    """
    
    max_leaves_per_year = models.IntegerField(
        default=20,
        help_text="Maximum number of leaves allowed per year"
    )
    
    leave_types = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        help_text="Leave types as JSON, e.g., {'sick': 10, 'casual': 5}"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leave_settings'
    
    def __str__(self):
        return f"Leave Settings: {self.max_leaves_per_year} max/year"


class ReportSetting(models.Model):
    """
    Report configuration settings.
    """
    
    report_type = models.CharField(max_length=100, unique=True, db_index=True)
    
    default_filters = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        help_text="Default filters for this report type"
    )
    
    access_roles = models.JSONField(
        null=True,
        blank=True,
        default=list,
        help_text="Roles that can access this report, e.g., ['ADMIN', 'MANAGER']"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'report_settings'
        ordering = ['report_type']
    
    def __str__(self):
        return f"Report Settings: {self.report_type}"


class SupportTicket(models.Model):
    """
    Support ticket model for user support.
    """
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('CLOSED', 'Closed'),
        ('PENDING', 'Pending'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='support_tickets'
    )
    
    subject = models.CharField(max_length=200)
    description = models.TextField()
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='OPEN',
        db_index=True
    )
    
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
        db_index=True
    )
    
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        limit_choices_to={'role__in': ['MANAGER', 'ADMIN']}
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'support_tickets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Ticket: {self.subject} - {self.user.work_id}"


class QualityCheck(models.Model):
    """
    Quality check model for images, JSON data, and final results.
    """
    
    STATUS_CHOICES = [
        ('PASS', 'Pass'),
        ('FAIL', 'Fail'),
        ('PENDING', 'Pending'),
    ]
    
    checked_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quality_checks_performed',
        limit_choices_to={'role__in': ['MANAGER', 'ADMIN']}
    )
    
    related_entity_type = models.CharField(
        max_length=50,
        db_index=True,
        help_text="e.g., 'STORE_VISIT', 'IMAGE'"
    )
    
    related_entity_id = models.IntegerField()
    
    image_url = models.ImageField(
        upload_to='quality_checks/',
        null=True,
        blank=True
    )
    
    json_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Structured quality check results"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True
    )
    
    comments = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quality_checks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['related_entity_type', 'related_entity_id']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Quality Check: {self.related_entity_type} #{self.related_entity_id} - {self.status}"
