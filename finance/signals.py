"""
Signal handlers for automatic points calculation.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from operations.models import StoreVisit, Image
from .services import PointsCalculationService


@receiver(post_save, sender=StoreVisit)
def calculate_visit_points(sender, instance, created, **kwargs):
    """
    Automatically calculate and award points when a store visit is completed.
    """
    if instance.status == 'COMPLETED':
        # Award points for completed visit
        PointsCalculationService.award_visit_points(instance)
    elif instance.status == 'SKIPPED':
        # Deduct points for skipped visit
        PointsCalculationService.deduct_missed_visit_points(instance)


@receiver(post_save, sender=Image)
def recalculate_visit_points_on_image_quality_change(sender, instance, created, **kwargs):
    """
    Recalculate visit points when image quality status changes.
    """
    if not created and instance.store_visit and instance.store_visit.status == 'COMPLETED':
        # Get previous quality status
        previous_status = None
        if instance.pk:
            try:
                old_instance = Image.objects.get(pk=instance.pk)
                previous_status = old_instance.quality_status
            except Image.DoesNotExist:
                pass
        
        # If quality status changed, recalculate points
        if previous_status and previous_status != instance.quality_status:
            PointsCalculationService.recalculate_visit_points(instance.store_visit)

