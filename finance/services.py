"""
Points calculation service for rewards and penalties system.
"""
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

from finance.models import UserPoints, PointsTransaction
from administration.models import Penalty


class PointsCalculationService:
    """
    Service for calculating and awarding points based on store visits and image quality.
    """
    
    # Point constants
    POINTS_PER_VISIT = 100
    PERFECT_VISIT_BONUS = 50
    IMAGE_QUALITY_BONUS = 25
    IMAGE_REJECTION_PENALTY = 30
    
    # Penalty constants
    BASE_MISSED_VISIT_PENALTY = 50
    HIGH_PRIORITY_MULTIPLIER = 2.0
    MEDIUM_PRIORITY_MULTIPLIER = 1.5
    LOW_PRIORITY_MULTIPLIER = 1.0
    
    # Financial penalty constants (SAR)
    BASE_FINANCIAL_PENALTY = Decimal('50.00')
    HIGH_PRIORITY_FINANCIAL_MULTIPLIER = Decimal('2.0')
    MEDIUM_PRIORITY_FINANCIAL_MULTIPLIER = Decimal('1.5')
    
    @classmethod
    def get_or_create_user_points(cls, user):
        """Get or create UserPoints instance for a user."""
        user_points, created = UserPoints.objects.get_or_create(user=user)
        return user_points
    
    @classmethod
    def calculate_image_quality_points(cls, store_visit):
        """
        Calculate points based on image quality acceptance rate.
        
        Returns:
            tuple: (total_points, activity_type, description)
        """
        images = store_visit.images.all()
        
        if not images.exists():
            # No images uploaded - just base visit completion
            return cls.POINTS_PER_VISIT, 'VISIT_COMPLETION', 'Visit completed'
        
        approved_count = images.filter(quality_status='APPROVED').count()
        rejected_count = images.filter(quality_status='REJECTED').count()
        total_count = images.count()
        
        if total_count == 0:
            return cls.POINTS_PER_VISIT, 'VISIT_COMPLETION', 'Visit completed'
        
        acceptance_rate = approved_count / total_count
        
        # Perfect visit (all images approved)
        if acceptance_rate == 1.0 and total_count > 0:
            total_points = cls.POINTS_PER_VISIT + cls.PERFECT_VISIT_BONUS
            return total_points, 'PERFECT_VISIT', f'Perfect visit - all {total_count} images approved'
        
        # High quality (80%+ approved)
        elif acceptance_rate >= 0.8:
            total_points = cls.POINTS_PER_VISIT + cls.IMAGE_QUALITY_BONUS
            return total_points, 'IMAGE_QUALITY_BONUS', f'High quality visit - {approved_count}/{total_count} images approved'
        
        # Low quality (<50% approved)
        elif acceptance_rate < 0.5:
            total_points = cls.POINTS_PER_VISIT - cls.IMAGE_REJECTION_PENALTY
            return total_points, 'IMAGE_REJECTION_PENALTY', f'Low quality visit - {rejected_count}/{total_count} images rejected'
        
        # Standard visit (50-80% approved)
        else:
            return cls.POINTS_PER_VISIT, 'VISIT_COMPLETION', f'Visit completed - {approved_count}/{total_count} images approved'
    
    @classmethod
    @transaction.atomic
    def award_visit_points(cls, store_visit):
        """
        Award points for a completed store visit.
        Calculates points based on visit completion and image quality.
        """
        if store_visit.status != 'COMPLETED':
            return None
        
        user = store_visit.user
        user_points = cls.get_or_create_user_points(user)
        
        # Calculate points based on image quality
        points, activity_type, description = cls.calculate_image_quality_points(store_visit)
        
        # Add points to user balance
        user_points.add_points(points, transaction_type='EARNED')
        
        # Create points transaction record
        transaction_record = PointsTransaction.objects.create(
            user=user,
            transaction_type='EARNED',
            activity_type=activity_type,
            points=points,
            description=description,
            store_visit=store_visit,
            store=store_visit.store,
            route=store_visit.route
        )
        
        return transaction_record
    
    @classmethod
    def calculate_missed_visit_penalty(cls, store):
        """
        Calculate penalty points and financial amount for a missed visit.
        
        Returns:
            tuple: (points_deducted, financial_amount, activity_type)
        """
        if store.priority == 'HIGH':
            points_deducted = int(cls.BASE_MISSED_VISIT_PENALTY * cls.HIGH_PRIORITY_MULTIPLIER)
            financial_amount = cls.BASE_FINANCIAL_PENALTY * cls.HIGH_PRIORITY_FINANCIAL_MULTIPLIER
            activity_type = 'HIGH_PRIORITY_MISSED'
        elif store.priority == 'MEDIUM':
            points_deducted = int(cls.BASE_MISSED_VISIT_PENALTY * cls.MEDIUM_PRIORITY_MULTIPLIER)
            financial_amount = cls.BASE_FINANCIAL_PENALTY * cls.MEDIUM_PRIORITY_FINANCIAL_MULTIPLIER
            activity_type = 'MISSED_VISIT_PENALTY'
        else:  # LOW
            points_deducted = int(cls.BASE_MISSED_VISIT_PENALTY * cls.LOW_PRIORITY_MULTIPLIER)
            financial_amount = cls.BASE_FINANCIAL_PENALTY
            activity_type = 'MISSED_VISIT_PENALTY'
        
        return points_deducted, financial_amount, activity_type
    
    @classmethod
    @transaction.atomic
    def deduct_missed_visit_points(cls, store_visit):
        """
        Deduct points and create penalty for a missed store visit.
        """
        if store_visit.status != 'SKIPPED':
            return None
        
        user = store_visit.user
        store = store_visit.store
        user_points = cls.get_or_create_user_points(user)
        
        # Calculate penalty
        points_deducted, financial_amount, activity_type = cls.calculate_missed_visit_penalty(store)
        
        # Deduct points from user balance
        user_points.deduct_points(points_deducted)
        
        # Create penalty record
        penalty = Penalty.objects.create(
            user=user,
            route=store_visit.route,
            store=store,
            reason=f"Missed visit to {store.name} ({store.get_priority_display()})",
            amount=financial_amount,
            points_deducted=points_deducted,
            penalty_type='FINANCIAL',
            store_visit=store_visit,
            status='ISSUED'
        )
        
        # Create points transaction record
        transaction_record = PointsTransaction.objects.create(
            user=user,
            transaction_type='DEDUCTED',
            activity_type=activity_type,
            points=-points_deducted,
            description=f"Missed visit penalty for {store.name} ({store.get_priority_display()})",
            store_visit=store_visit,
            store=store,
            route=store_visit.route
        )
        
        return penalty, transaction_record
    
    @classmethod
    def recalculate_visit_points(cls, store_visit):
        """
        Recalculate points for a visit when image quality status changes.
        This is useful when images are approved/rejected after visit completion.
        """
        if store_visit.status != 'COMPLETED':
            return None
        
        # Check if points were already awarded
        existing_transaction = PointsTransaction.objects.filter(
            store_visit=store_visit,
            transaction_type='EARNED'
        ).first()
        
        if not existing_transaction:
            # No points awarded yet, award them now
            return cls.award_visit_points(store_visit)
        
        # Recalculate points
        new_points, activity_type, description = cls.calculate_image_quality_points(store_visit)
        old_points = existing_transaction.points
        
        if new_points != old_points:
            # Points changed, update balance
            user = store_visit.user
            user_points = cls.get_or_create_user_points(user)
            
            # Adjust points
            points_diff = new_points - old_points
            if points_diff > 0:
                user_points.add_points(points_diff, transaction_type='EARNED')
            else:
                user_points.deduct_points(abs(points_diff))
            
            # Update transaction
            existing_transaction.points = new_points
            existing_transaction.activity_type = activity_type
            existing_transaction.description = description
            existing_transaction.save()
            
            return existing_transaction
        
        return existing_transaction

