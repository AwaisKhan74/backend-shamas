from datetime import timedelta

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from users.models import User
from core.models import Route, Store

# Lazy storage class that evaluates at runtime
class LazyS3Storage:
    """Lazy storage that uses S3 when enabled, otherwise default storage."""
    def __call__(self):
        if getattr(settings, 'USE_S3_STORAGE', False):
            from storages.backends.s3boto3 import S3Boto3Storage
            return S3Boto3Storage()
        from django.core.files.storage import default_storage
        return default_storage


class CheckIn(models.Model):
    """
    Represents a single field agent work session (check-in/out lifecycle).
    """

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", _("Active")
        ON_BREAK = "ON_BREAK", _("On Break")
        COMPLETED = "COMPLETED", _("Completed")

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='check_ins',
        limit_choices_to={'role': 'FIELD_AGENT'}
    )

    shift_date = models.DateField(
        default=timezone.localdate,
        db_index=True,
        help_text="Calendar date associated with this work session."
    )

    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="Check-in timestamp when the work session started."
    )

    # GPS coordinates
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ]
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ]
    )

    check_out_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp recorded when the agent checked out."
    )

    check_out_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ],
        help_text="Latitude captured at checkout."
    )

    check_out_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ],
        help_text="Longitude captured at checkout."
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True
    )

    current_break_start = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Start timestamp for an ongoing break."
    )

    total_break_duration = models.DurationField(
        default=timedelta,
        help_text="Cumulative duration of all breaks taken during the session."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'check_ins'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['user', 'shift_date', 'status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'shift_date'],
                name='unique_shift_per_user_per_day'
            ),
        ]

    def __str__(self):
        return f"Check-in: {self.user.work_id} - {self.timestamp}"

    @property
    def is_active(self):
        return self.status in {self.Status.ACTIVE, self.Status.ON_BREAK} and not self.check_out_time
    
    @property
    def total_hours_worked(self):
        """Calculate total hours worked (excluding breaks)."""
        if not self.check_out_time:
            # If not checked out, calculate from start to now (minus breaks)
            now = timezone.now()
            if self.current_break_start:
                # If on break, don't count break time
                total_time = (self.current_break_start - self.timestamp) - self.total_break_duration
            else:
                total_time = (now - self.timestamp) - self.total_break_duration
        else:
            # If checked out, calculate from start to checkout (minus breaks)
            total_time = (self.check_out_time - self.timestamp) - self.total_break_duration
        
        return total_time.total_seconds() / 3600.0  # Convert to hours
    
    @property
    def total_hours_worked_seconds(self):
        """Get total hours worked in seconds."""
        if not self.check_out_time:
            now = timezone.now()
            if self.current_break_start:
                total_time = (self.current_break_start - self.timestamp) - self.total_break_duration
            else:
                total_time = (now - self.timestamp) - self.total_break_duration
        else:
            total_time = (self.check_out_time - self.timestamp) - self.total_break_duration
        
        return int(total_time.total_seconds())
    
    @property
    def break_duration_hours(self):
        """Get total break duration in hours."""
        if self.total_break_duration:
            return self.total_break_duration.total_seconds() / 3600.0
        return 0.0
    
    @property
    def break_duration_seconds(self):
        """Get total break duration in seconds."""
        if self.total_break_duration:
            return int(self.total_break_duration.total_seconds())
        return 0
    
    @property
    def remaining_shift_hours(self):
        """Calculate remaining shift hours (9 hours total shift)."""
        SHIFT_HOURS = 9.0
        worked = self.total_hours_worked
        remaining = SHIFT_HOURS - worked
        return max(0.0, remaining)  # Don't return negative
    
    @property
    def remaining_shift_seconds(self):
        """Get remaining shift time in seconds."""
        return int(self.remaining_shift_hours * 3600)

    def start_break(self, start_time=None):
        if self.status == self.Status.COMPLETED:
            raise ValueError("Completed sessions cannot start a break.")
        if self.current_break_start:
            raise ValueError("A break is already in progress.")
        self.current_break_start = start_time or timezone.now()
        self.status = self.Status.ON_BREAK
        self.save(update_fields=['current_break_start', 'status', 'updated_at'])

    def resume_from_break(self, end_time=None):
        if not self.current_break_start:
            raise ValueError("No active break to resume from.")
        end_time = end_time or timezone.now()
        duration = end_time - self.current_break_start
        self.total_break_duration += duration
        self.current_break_start = None
        self.status = self.Status.ACTIVE
        self.save(update_fields=['current_break_start', 'total_break_duration', 'status', 'updated_at'])
        return duration

    def mark_check_out(self, checkout_time=None, latitude=None, longitude=None):
        if self.check_out_time:
            raise ValueError("Session already checked out.")
        if self.current_break_start:
            raise ValueError("Cannot checkout while a break is in progress.")
        checkout_time = checkout_time or timezone.now()
        self.check_out_time = checkout_time
        if latitude is not None:
            self.check_out_latitude = latitude
        if longitude is not None:
            self.check_out_longitude = longitude
        self.status = self.Status.COMPLETED
        self.save(
            update_fields=[
                'check_out_time',
                'check_out_latitude',
                'check_out_longitude',
                'status',
                'updated_at'
            ]
        )
        return checkout_time


class Break(models.Model):
    """
    Break model for tracking breaks during route execution.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='breaks',
        limit_choices_to={'role': 'FIELD_AGENT'}
    )

    session = models.ForeignKey(
        CheckIn,
        on_delete=models.CASCADE,
        related_name='break_entries',
        help_text="Work session this break belongs to.",
        null=True,
        blank=True
    )

    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='breaks',
        null=True,
        blank=True
    )

    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)

    # Duration calculated automatically
    duration = models.DurationField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'breaks'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['session', 'start_time']),
            models.Index(fields=['user', 'route']),
            models.Index(fields=['start_time']),
        ]
    
    def __str__(self):
        route_info = f" - Route {self.route.id}" if self.route else ""
        return f"Break: {self.user.work_id}{route_info}"
    
    def calculate_duration(self):
        """Calculate break duration if end_time is set."""
        if self.end_time:
            self.duration = self.end_time - self.start_time
            return self.duration
        return None
    
    def save(self, *args, **kwargs):
        """Override save to calculate duration."""
        if self.end_time:
            self.calculate_duration()
        super().save(*args, **kwargs)


class StoreVisit(models.Model):
    """
    Store visit model for tracking individual store visits during routes.
    """
    
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('SKIPPED', 'Skipped'),
        ('FLAGGED', 'Flagged'),
    ]
    
    AI_ML_CHECK_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('MANUAL_REVIEW', 'Manual Review'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='store_visits',
        limit_choices_to={'role': 'FIELD_AGENT'}
    )
    
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='store_visits'
    )
    
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='visits'
    )
    
    # Entry/Exit tracking
    entry_time = models.DateTimeField(null=True, blank=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    
    # GPS coordinates for entry
    entry_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ]
    )
    
    entry_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ]
    )
    
    # GPS coordinates for exit
    exit_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ]
    )
    
    exit_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ]
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='IN_PROGRESS',
        db_index=True
    )
    
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    # Approval
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_store_visits',
        limit_choices_to={'role': 'MANAGER'}
    )
    
    # AI/ML Check
    ai_ml_check_status = models.CharField(
        max_length=20,
        choices=AI_ML_CHECK_STATUS_CHOICES,
        default='PENDING',
        db_index=True
    )
    
    ai_ml_feedback = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'store_visits'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'route']),
            models.Index(fields=['store', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['ai_ml_check_status']),
        ]
    
    def __str__(self):
        return f"Visit: {self.user.work_id} - {self.store.name} - {self.status}"


class Image(models.Model):
    """
    Image model for storing images captured during store visits.
    """
    
    IMAGE_TYPE_CHOICES = [
        ('PRODUCT', 'Product'),
        ('STOREFRONT', 'Storefront'),
        ('OTHER', 'Other'),
    ]
    
    QUALITY_STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    store_visit = models.ForeignKey(
        StoreVisit,
        on_delete=models.CASCADE,
        related_name='images'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='captured_images'
    )
    
    image_url = models.ImageField(
        upload_to='store_visit_images/',
        storage=LazyS3Storage(),
        help_text="Image captured during store visit"
    )
    
    captured_at = models.DateTimeField(default=timezone.now)
    
    image_type = models.CharField(
        max_length=20,
        choices=IMAGE_TYPE_CHOICES,
        default='OTHER'
    )
    
    quality_status = models.CharField(
        max_length=20,
        choices=QUALITY_STATUS_CHOICES,
        default='PENDING',
        db_index=True,
        help_text="Image quality approval status"
    )
    
    quality_checked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quality_checked_images',
        limit_choices_to={'role__in': ['MANAGER', 'ADMIN']},
        help_text="User who approved/rejected this image"
    )
    
    quality_checked_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'images'
        ordering = ['-captured_at']
        indexes = [
            models.Index(fields=['store_visit', 'captured_at']),
            models.Index(fields=['image_type']),
            models.Index(fields=['quality_status']),
        ]
    
    def __str__(self):
        return f"Image: {self.store_visit.store.name} - {self.image_type}"


class PermissionForm(models.Model):
    """
    Permission form model for store visit permission forms.
    Captures store representative information and permission confirmation.
    """
    
    store_visit = models.OneToOneField(
        StoreVisit,
        on_delete=models.CASCADE,
        related_name='permission_form'
    )
    
    # Store Representative Information
    representative_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Store representative name"
    )
    
    representative_designation = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Store representative designation"
    )
    
    representative_contact = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Store representative contact number (optional)"
    )
    
    # Permission Question
    permission_received = models.BooleanField(
        null=True,
        blank=True,
        help_text="Has permission been received to start counting?"
    )
    
    # Signature (stored as file reference)
    signature = models.ForeignKey(
        'core.FileManager',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='permission_form_signatures',
        help_text="Signature image (optional)"
    )
    
    # Counter Confirmations (optional checkboxes)
    permission_granted_confirmed = models.BooleanField(
        default=False,
        help_text="Counter confirms permission has been granted"
    )
    
    representative_details_verified = models.BooleanField(
        default=False,
        help_text="Counter has verified representative details"
    )
    
    ready_to_begin_collection = models.BooleanField(
        default=False,
        help_text="Counter is ready to begin data collection"
    )
    
    # Status
    is_flagged = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether this store visit was flagged"
    )
    
    # Keep form_data for backward compatibility and additional data
    form_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional flexible form data storage"
    )
    
    submitted_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'permission_forms'
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['is_flagged']),
            models.Index(fields=['submitted_at']),
        ]
    
    def __str__(self):
        return f"Permission Form: {self.store_visit.store.name}"


class FlaggedStore(models.Model):
    """
    Model for tracking flagged stores with reasons.
    Stores are flagged when permission is not received or other issues occur.
    """
    
    REASON_CHOICES = [
        ('STORE_CLOSED_PERMANENTLY', 'Store closed permanently'),
        ('ACCESS_DENIED', 'Access denied'),
        ('WRONG_LOCATION_DUPLICATE', 'Wrong location or duplicate'),
        ('INVENTORY_ISSUE', 'Inventory issue'),
        ('OTHER', 'Other'),
    ]
    
    store_visit = models.OneToOneField(
        StoreVisit,
        on_delete=models.CASCADE,
        related_name='flagged_store',
        help_text="Store visit that was flagged"
    )
    
    reason = models.CharField(
        max_length=50,
        choices=REASON_CHOICES,
        db_index=True,
        help_text="Reason for flagging the store"
    )
    
    additional_details = models.TextField(
        null=True,
        blank=True,
        help_text="Additional details about why the store was flagged"
    )
    
    flagged_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='flagged_stores',
        help_text="User who flagged the store"
    )
    
    flagged_at = models.DateTimeField(auto_now_add=True)
    
    # Resolution
    is_resolved = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether the flag has been resolved"
    )
    
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_flags',
        limit_choices_to={'role__in': ['MANAGER', 'ADMIN']},
        help_text="Manager/admin who resolved the flag"
    )
    
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'flagged_stores'
        ordering = ['-flagged_at']
        indexes = [
            models.Index(fields=['reason']),
            models.Index(fields=['is_resolved']),
            models.Index(fields=['flagged_at']),
        ]
    
    def __str__(self):
        return f"Flagged: {self.store_visit.store.name} - {self.get_reason_display()}"
