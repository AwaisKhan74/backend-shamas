"""
Signal handlers for automatic notification creation.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from leaves.models import LeaveRequest
from administration.models import Penalty
from core.models import Route
from operations.models import Image, StoreVisit
from finance.models import PointsTransaction
from notifications.services import NotificationService

# Store old instances to track changes
_old_instances = {}


@receiver(post_save, sender=LeaveRequest)
def notify_leave_status_change(sender, instance, created, **kwargs):
    """Send notification when leave request status changes."""
    if not created and instance.status in ['APPROVED', 'REJECTED', 'CANCELLED']:
        NotificationService.create_leave_notification(instance, instance.status)


@receiver(post_save, sender=Penalty)
def notify_penalty_issued(sender, instance, created, **kwargs):
    """Send notification when penalty is issued."""
    if created:
        NotificationService.create_penalty_notification(instance)


@receiver(pre_save, sender=Route)
def store_old_route(sender, instance, **kwargs):
    """Store old route instance before save to track changes."""
    if instance.pk:
        try:
            _old_instances[instance.pk] = Route.objects.get(pk=instance.pk)
        except Route.DoesNotExist:
            _old_instances[instance.pk] = None


@receiver(post_save, sender=Route)
def notify_route_assigned_or_approved(sender, instance, created, **kwargs):
    """Send notification when route is assigned or approved."""
    if created and instance.user:
        # New route assigned
        NotificationService.create_route_notification(instance, 'ROUTE_ASSIGNED')
    elif not created:
        # Check if route was just approved
        old_instance = _old_instances.pop(instance.pk, None)
        if old_instance:
            # Check if status changed to APPROVED
            if (instance.status == 'APPROVED' and 
                old_instance.status != 'APPROVED' and 
                instance.approved_by):
                NotificationService.create_route_notification(instance, 'ROUTE_APPROVED')
        else:
            # Fallback: check update_fields
            update_fields = kwargs.get('update_fields', None)
            if update_fields:
                if 'status' in update_fields and instance.status == 'APPROVED':
                    NotificationService.create_route_notification(instance, 'ROUTE_APPROVED')
                elif 'approved_by' in update_fields and instance.approved_by:
                    NotificationService.create_route_notification(instance, 'ROUTE_APPROVED')


@receiver(pre_save, sender=Image)
def store_old_image(sender, instance, **kwargs):
    """Store old image instance before save to track changes."""
    if instance.pk:
        try:
            _old_instances[instance.pk] = Image.objects.get(pk=instance.pk)
        except Image.DoesNotExist:
            _old_instances[instance.pk] = None


@receiver(post_save, sender=Image)
def notify_image_quality_check(sender, instance, created, **kwargs):
    """Send notification when image quality status changes."""
    if not created and instance.quality_status in ['APPROVED', 'REJECTED']:
        old_instance = _old_instances.pop(instance.pk, None)
        if old_instance and old_instance.quality_status != instance.quality_status:
            # Status changed
            NotificationService.create_quality_check_notification(instance, instance.quality_status)
        elif not old_instance:
            # Fallback: check update_fields
            update_fields = kwargs.get('update_fields', None)
            if update_fields and 'quality_status' in update_fields:
                NotificationService.create_quality_check_notification(instance, instance.quality_status)


@receiver(post_save, sender=PointsTransaction)
def notify_points_transaction(sender, instance, created, **kwargs):
    """Send notification for points transactions."""
    if created and abs(instance.points) > 0:
        NotificationService.create_points_notification(
            user=instance.user,
            points=instance.points,
            activity_type=instance.activity_type,
            description=instance.description
        )


@receiver(pre_save, sender=StoreVisit)
def store_old_store_visit(sender, instance, **kwargs):
    """Store old store visit instance before save to track changes."""
    if instance.pk:
        try:
            _old_instances[instance.pk] = StoreVisit.objects.get(pk=instance.pk)
        except StoreVisit.DoesNotExist:
            _old_instances[instance.pk] = None


@receiver(post_save, sender=StoreVisit)
def notify_store_visit_status_change(sender, instance, created, **kwargs):
    """Send notification when store visit status changes."""
    if created and instance.status == 'FLAGGED':
        # If visit is created as FLAGGED
        NotificationService.create_store_visit_notification(instance, 'STORE_VISIT_FLAGGED')
    elif not created:
        old_instance = _old_instances.pop(instance.pk, None)
        if old_instance and old_instance.status != instance.status:
            # Status changed
            if instance.status == 'COMPLETED':
                NotificationService.create_store_visit_notification(instance, 'STORE_VISIT_COMPLETED')
            elif instance.status == 'FLAGGED':
                NotificationService.create_store_visit_notification(instance, 'STORE_VISIT_FLAGGED')
        elif not old_instance:
            # Fallback: check update_fields
            update_fields = kwargs.get('update_fields', None)
            if update_fields and 'status' in update_fields:
                if instance.status == 'COMPLETED':
                    NotificationService.create_store_visit_notification(instance, 'STORE_VISIT_COMPLETED')
                elif instance.status == 'FLAGGED':
                    NotificationService.create_store_visit_notification(instance, 'STORE_VISIT_FLAGGED')

