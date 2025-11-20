from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


class ActiveUserManager(UserManager):
    """Default manager returning only non-deleted users."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Supports three roles: FIELD_AGENT, MANAGER, and ADMIN.
    """
    
    ROLE_CHOICES = [
        ('FIELD_AGENT', 'Field Agent'),
        ('MANAGER', 'Manager'),
        ('ADMIN', 'Admin'),
    ]
    
    # Work ID - unique identifier for employees
    work_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique work identification number"
    )
    
    # Role-based access control
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='FIELD_AGENT',
        db_index=True
    )
    
    # Contact information
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )

    # Profile & contact details
    display_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="Public display name"
    )

    STATUS_CHOICES = [
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
        ('AWAY', 'Away'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='OFFLINE',
        db_index=True,
        help_text="Current availability status"
    )

    country = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Country or region"
    )

    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="City"
    )

    address = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Address details"
    )

    # Profile picture
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True
    )
    
    # Permission flags (for mobile app)
    has_gps_permission = models.BooleanField(default=False)
    has_camera_permission = models.BooleanField(default=False)
    
    # Notification & app preference flags
    push_notifications_enabled = models.BooleanField(default=False)
    route_reminders_enabled = models.BooleanField(default=False)
    reward_alerts_enabled = models.BooleanField(default=False)
    qc_alerts_enabled = models.BooleanField(default=False)

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ar', 'Arabic'),
    ]

    preferred_language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default='en',
        help_text="Preferred language code"
    )

    # Additional metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Override email to make it required
    email = models.EmailField(unique=True)
    
    objects = ActiveUserManager()
    all_objects = UserManager()

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['work_id']),
            models.Index(fields=['role']),
            models.Index(fields=['email']),
            models.Index(fields=['is_deleted']),
        ]
    
    def __str__(self):
        return f"{self.work_id} - {self.get_full_name() or self.username}"
    
    @property
    def is_field_agent(self):
        """Check if user is a field agent."""
        return self.role == 'FIELD_AGENT'
    
    @property
    def is_manager(self):
        """Check if user is a manager."""
        return self.role == 'MANAGER'
    
    @property
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == 'ADMIN'

    def soft_delete(self):
        """Soft delete the user by flagging as deleted and deactivating."""
        if not self.is_deleted:
            self.is_active = False
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(update_fields=['is_active', 'is_deleted', 'deleted_at'])
