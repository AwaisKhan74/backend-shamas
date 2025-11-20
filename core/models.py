import hashlib
import mimetypes
import os
from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from users.models import User

# Get storage backend
def get_file_storage():
    """Get storage backend from DEFAULT_FILE_STORAGE setting."""
    storage_path = getattr(settings, 'DEFAULT_FILE_STORAGE', 'django.core.files.storage.FileSystemStorage')
    
    if 'storages.backends.s3boto3.S3Boto3Storage' in storage_path:
        from storages.backends.s3boto3 import S3Boto3Storage
        return S3Boto3Storage()
    else:
        from django.core.files.storage import FileSystemStorage
        return FileSystemStorage()


class Counter(models.Model):
    """
    Counter/Field Agent profile model.
    Each counter is linked to a User via OneToOne relationship.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='counter_profile',
        limit_choices_to={'role': 'FIELD_AGENT'}
    )
    
    employee_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique employee identification number"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'counters'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee_id']),
        ]
    
    @property
    def is_active(self):
        """Use the User's is_active field from AbstractUser."""
        return self.user.is_active if self.user else False
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name() or self.user.username}"


class District(models.Model):
    """
    District model representing geographical districts.
    Stores belong to districts, and routes can be district-specific.
    """
    
    PRIORITY_CHOICES = [
        ('HIGH', 'High Priority'),
        ('MEDIUM', 'Medium Priority'),
        ('LOW', 'Low Priority'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    ]
    
    name = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        help_text="District name (e.g., 'Al Naseem', 'Al Rawdah')"
    )
    
    code = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text="Optional district code/abbreviation"
    )
    
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
        db_index=True,
        help_text="Priority level for district operations"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        db_index=True
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Additional information about the district"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'districts'
        ordering = ['name']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_priority_display()})"


class Store(models.Model):
    """
    Store model representing physical store locations.
    """
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    ]
    
    PRIORITY_CHOICES = [
        ('HIGH', 'High Priority'),
        ('MEDIUM', 'Medium Priority'),
        ('LOW', 'Low Priority'),
    ]
    
    name = models.CharField(max_length=200)
    address = models.TextField()
    
    # District relationship
    district = models.ForeignKey(
        'District',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='stores',
        help_text="District this store belongs to"
    )
    
    # GPS coordinates
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ],
        help_text="Latitude coordinate"
    )
    
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ],
        help_text="Longitude coordinate"
    )
    
    # Contact information
    contact_person = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
        db_index=True,
        help_text="Store priority level (affects penalty calculation for missed visits)"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        db_index=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stores'
        ordering = ['name']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['district']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.address[:50]}"


class Route(models.Model):
    """
    Route model representing daily routes assigned to field agents.
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('STARTED', 'Started'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    
    # District relationship
    district = models.ForeignKey(
        'District',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='routes',
        help_text="District this route is specific to (optional)"
    )
    
    # Assignment
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_routes',
        limit_choices_to={'role': 'FIELD_AGENT'},
        help_text="Field agent assigned to this route"
    )
    
    date = models.DateField(db_index=True)
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True
    )
    
    # Timing
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    # Approval
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_routes',
        limit_choices_to={'role': 'MANAGER'},
        help_text="Manager who approved this route"
    )
    
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'routes'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['status']),
            models.Index(fields=['date']),
            models.Index(fields=['district']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.user.work_id} - {self.date}"


class RouteStore(models.Model):
    """
    Many-to-Many through model linking Routes and Stores.
    Defines the order/priority of stores within a route.
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('VISITED', 'Visited'),
        ('SKIPPED', 'Skipped'),
    ]
    
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='route_stores'
    )
    
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='route_stores'
    )
    
    order = models.IntegerField(
        default=1,
        help_text="Order/priority of store in the route"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'route_stores'
        ordering = ['route', 'order']
        unique_together = [['route', 'store']]
        indexes = [
            models.Index(fields=['route', 'order']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.route.name} - {self.store.name} (Order: {self.order})"


class FileManager(models.Model):
    """
    File Manager model for centralized file management backed by object storage.
    Records capture purpose, uploader, and storage metadata to aid reuse across the app.
    """

    FILE_TYPE_CHOICES = [
        ('IMAGE', 'Image'),
        ('DOCUMENT', 'Document'),
        ('VIDEO', 'Video'),
        ('OTHER', 'Other'),
    ]

    PURPOSE_CHOICES = [
        ('GENERAL', 'General'),
        ('PROFILE_IMAGE', 'Profile Image'),
        ('ROUTE_ATTACHMENT', 'Route Attachment'),
        ('REPORT_ATTACHMENT', 'Report Attachment'),
        ('USER_DOCUMENT', 'User Document'),
        ('PERMISSION_FORM_SIGNATURE', 'Permission Form Signature'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='managed_files',
        help_text="User who uploaded the file"
    )
    
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name='files',
        null=True,
        blank=True,
        help_text="Route associated with this file (optional)"
    )

    purpose = models.CharField(
        max_length=50,
        choices=PURPOSE_CHOICES,
        default='GENERAL',
        db_index=True,
        help_text="Business purpose or usage context for this file"
    )

    file = models.FileField(
        upload_to='file_manager/%Y/%m/%d/',
        storage=get_file_storage(),
        help_text="Uploaded file stored in object storage"
    )

    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPE_CHOICES,
        default='IMAGE',
        db_index=True,
        help_text="Type of file"
    )

    description = models.TextField(
        null=True,
        blank=True,
        help_text="Description or notes about the file"
    )
    
    file_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Original file name"
    )
    
    file_size = models.IntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )

    bucket = models.CharField(
        max_length=255,
        blank=True,
        help_text="Object storage bucket where the file is stored (auto-populated)"
    )

    object_key = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        help_text="Full object key/path within the storage bucket (auto-populated)"
    )

    content_type = models.CharField(
        max_length=127,
        blank=True,
        help_text="MIME type detected for this file"
    )

    checksum = models.CharField(
        max_length=128,
        blank=True,
        help_text="Checksum (MD5) of the stored file for integrity validation"
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether the file is active/visible"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'file_manager'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['route', 'created_at']),
            models.Index(fields=['file_type']),
            models.Index(fields=['purpose']),
            models.Index(fields=['is_active']),
            models.Index(fields=['bucket']),
        ]
    
    def __str__(self):
        route_info = f" - Route: {self.route.name}" if self.route else ""
        return f"File: {self.file_name or 'N/A'} - User: {self.user.work_id}{route_info}"
    
    def save(self, *args, **kwargs):
        """
        Override save to extract file metadata using django-storages.
        django-storages handles the actual file upload to S3 automatically.
        """
        # Check if this is a new file or if file has changed
        file_changed = False
        if self.pk:
            try:
                old_instance = self.__class__.objects.get(pk=self.pk)
                file_changed = old_instance.file != self.file
            except self.__class__.DoesNotExist:
                file_changed = True
        else:
            file_changed = True
        
        # Extract metadata before saving (for new or changed files)
        if self.file and (file_changed or not self.file_name):
            # Get original filename from uploaded file
            if hasattr(self.file, 'name'):
                # For uploaded files, get the original name
                original_name = getattr(self.file, 'name', None)
                if original_name and not self.file_name:
                    # Extract just the filename without path
                    self.file_name = os.path.basename(original_name)
            
            # Get file size
            if hasattr(self.file, 'size') and not self.file_size:
                self.file_size = self.file.size
            elif hasattr(self.file, 'file') and hasattr(self.file.file, 'size') and not self.file_size:
                self.file_size = self.file.file.size
            
            # Detect content type
            if not self.content_type:
                # Try to get from file object
                if hasattr(self.file, 'content_type'):
                    self.content_type = self.file.content_type
                elif hasattr(self.file, 'file') and hasattr(self.file.file, 'content_type'):
                    self.content_type = self.file.file.content_type
                else:
                    # Fallback to mimetypes
                    file_name = getattr(self.file, 'name', '')
                    if file_name:
                        guessed_type, _ = mimetypes.guess_type(file_name)
                        if guessed_type:
                            self.content_type = guessed_type

        # Save the model first (django-storages will handle file upload)
        super().save(*args, **kwargs)

        # Extract storage metadata after save (when file is actually stored)
        if self.file:
            updated_fields = []
            
            # Get object key/path from storage
            # django-storages stores the file and self.file.name contains the storage path
            if self.file.name and (not self.object_key or self.object_key != self.file.name):
                self.object_key = self.file.name
                updated_fields.append('object_key')
            
            # Get bucket name from storage backend
            if not self.bucket:
                storage = self.file.storage
                # For S3Boto3Storage, get bucket from storage
                if hasattr(storage, 'bucket_name'):
                    self.bucket = storage.bucket_name
                    updated_fields.append('bucket')
                elif hasattr(settings, 'AWS_STORAGE_BUCKET_NAME') and settings.AWS_STORAGE_BUCKET_NAME:
                    self.bucket = settings.AWS_STORAGE_BUCKET_NAME
                    updated_fields.append('bucket')
            
            # Calculate checksum if file is accessible
            if not self.checksum and self.file:
                try:
                    # Open file and calculate MD5
                    self.file.open('rb')
                    hash_md5 = hashlib.md5()
                    for chunk in self.file.chunks():
                        hash_md5.update(chunk)
                    self.checksum = hash_md5.hexdigest()
                    updated_fields.append('checksum')
                    self.file.close()
                except Exception:
                    # If checksum calculation fails, continue without it
                    pass

            # Update metadata fields if needed
            if updated_fields:
                super().save(update_fields=updated_fields)
    
    @property
    def file_url(self):
        """Return the URL of the file."""
        if self.file:
            return self.file.url
        return None

    @property
    def file_size_mb(self):
        """Approximate file size in megabytes (two decimal places)."""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None


