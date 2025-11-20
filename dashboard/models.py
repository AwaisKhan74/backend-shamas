from django.db import models
from users.models import User


class InsightPanel(models.Model):
    """
    Insight panel model for interactive dashboard cards/panels.
    """
    
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    
    configuration = models.JSONField(
        default=dict,
        help_text="Display settings and configuration"
    )
    
    data_source = models.CharField(
        max_length=200,
        help_text="Source of data for this panel"
    )
    
    access_roles = models.JSONField(
        null=True,
        blank=True,
        default=list,
        help_text="Roles that can view this panel, e.g., ['ADMIN', 'MANAGER']"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_insight_panels',
        limit_choices_to={'role': 'ADMIN'}
    )
    
    is_active = models.BooleanField(default=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'insight_panels'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.data_source}"


class Dataset(models.Model):
    """
    Dataset model for filtering and data behavior.
    """
    
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    
    schema = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        help_text="Dataset schema definition"
    )
    
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_datasets'
    )
    
    access_roles = models.JSONField(
        null=True,
        blank=True,
        default=list,
        help_text="Roles that can access this dataset"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'datasets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.owner.work_id}"


class DownloadableFile(models.Model):
    """
    Downloadable file model for download center.
    """
    
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    
    file = models.FileField(
        upload_to='downloadable_files/',
        help_text="File available for download"
    )
    
    file_type = models.CharField(
        max_length=50,
        help_text="File type/category"
    )
    
    size = models.IntegerField(
        help_text="File size in bytes"
    )
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_files',
        limit_choices_to={'role__in': ['MANAGER', 'ADMIN']}
    )
    
    access_roles = models.JSONField(
        null=True,
        blank=True,
        default=list,
        help_text="Roles that can download this file"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'downloadable_files'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['file_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.file_type}"


class DownloadHistory(models.Model):
    """
    Download history model for tracking file downloads.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='download_history'
    )
    
    file = models.ForeignKey(
        DownloadableFile,
        on_delete=models.CASCADE,
        related_name='download_history'
    )
    
    download_timestamp = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'download_history'
        ordering = ['-download_timestamp']
        indexes = [
            models.Index(fields=['user', 'download_timestamp']),
            models.Index(fields=['download_timestamp']),
        ]
    
    def __str__(self):
        return f"Download: {self.user.work_id} - {self.file.name}"


class FAQ(models.Model):
    """
    FAQ model for frequently asked questions.
    """
    
    question = models.TextField()
    answer = models.TextField()
    
    category = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Category for organizing FAQs"
    )
    
    is_active = models.BooleanField(default=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'faqs'
        ordering = ['category', 'question']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"FAQ: {self.question[:50]}..."
