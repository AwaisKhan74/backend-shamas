from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from users.models import User


class Notification(models.Model):
    """
    Notification model for in-app notifications.
    Supports polymorphic relationships to any model.
    """
    
    TYPE_CHOICES = [
        # Leave Management
        ('LEAVE_APPROVED', 'Leave Approved'),
        ('LEAVE_REJECTED', 'Leave Rejected'),
        ('LEAVE_CANCELLED', 'Leave Cancelled'),
        
        # Route Management
        ('ROUTE_ASSIGNED', 'Route Assigned'),
        ('ROUTE_APPROVED', 'Route Approved'),
        
        # Penalties & Rewards
        ('PENALTY_ISSUED', 'Penalty Issued'),
        ('REWARD_EARNED', 'Reward Earned'),
        ('POINTS_EARNED', 'Points Earned'),
        ('POINTS_DEDUCTED', 'Points Deducted'),
        
        # Store Visits
        ('STORE_VISIT_COMPLETED', 'Store Visit Completed'),
        ('STORE_VISIT_FLAGGED', 'Store Visit Flagged'),
        
        # Quality Checks
        ('IMAGE_APPROVED', 'Image Approved'),
        ('IMAGE_REJECTED', 'Image Rejected'),
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
        related_name='notifications',
        db_index=True
    )
    
    notification_type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        db_index=True
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
        db_index=True
    )
    
    # Polymorphic relationship to any model
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # Additional data as JSON
    metadata = models.JSONField(default=dict, blank=True)
    
    # Read status
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'notification_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} - {self.user.work_id}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
