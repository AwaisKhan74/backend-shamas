from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from users.models import User


class Reward(models.Model):
    """
    Reward model defining reward types and configurations.
    """
    
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    
    points_required = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Points required to earn this reward"
    )
    
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Monetary value if applicable"
    )
    
    is_active = models.BooleanField(default=True, db_index=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_rewards',
        limit_choices_to={'role': 'ADMIN'}
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rewards'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.points_required} points"


class UserReward(models.Model):
    """
    User reward model tracking rewards awarded to users.
    """
    
    STATUS_CHOICES = [
        ('EARNED', 'Earned'),
        ('WITHDRAWN', 'Withdrawn'),
        ('EXPIRED', 'Expired'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rewards_awarded',
        limit_choices_to={'role': 'FIELD_AGENT'}
    )
    
    reward = models.ForeignKey(
        Reward,
        on_delete=models.CASCADE,
        related_name='user_rewards'
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Actual amount earned"
    )
    
    description = models.TextField(null=True, blank=True)
    
    earned_at = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='EARNED',
        db_index=True
    )
    
    awarded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rewards_given',
        limit_choices_to={'role__in': ['MANAGER', 'ADMIN']}
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_rewards'
        ordering = ['-earned_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['earned_at']),
        ]
    
    activity_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Activity that earned this reward (e.g., 'Perfect Visit', 'Visit Completion')"
    )
    
    points_earned = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Points earned from this activity"
    )
    
    store_visit = models.ForeignKey(
        'operations.StoreVisit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rewards_earned',
        help_text="Store visit that earned this reward"
    )
    
    def __str__(self):
        return f"Reward: {self.user.work_id} - {self.amount} - {self.status}"


class Withdrawal(models.Model):
    """
    Withdrawal model for tracking withdrawal requests for rewards.
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PROCESSED', 'Processed'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='withdrawals',
        limit_choices_to={'role': 'FIELD_AGENT'}
    )
    
    reward = models.ForeignKey(
        UserReward,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='withdrawals',
        help_text="Specific reward if linked"
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    request_date = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True
    )
    
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_withdrawals',
        limit_choices_to={'role': 'ADMIN'}
    )
    
    processed_at = models.DateTimeField(null=True, blank=True)
    
    transaction_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Transaction ID from payment processor"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'withdrawals'
        ordering = ['-request_date']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['request_date']),
        ]
    
    def __str__(self):
        return f"Withdrawal: {self.user.work_id} - {self.amount} - {self.status}"


class FinanceTransaction(models.Model):
    """
    Finance transaction model for tracking all financial transactions.
    """
    
    TRANSACTION_TYPE_CHOICES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
        ('REWARD_PAYOUT', 'Reward Payout'),
        ('PENALTY', 'Penalty'),
    ]
    
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        db_index=True
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    description = models.TextField(null=True, blank=True)
    
    related_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='finance_transactions'
    )
    
    related_entity_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="e.g., 'WITHDRAWAL', 'PENALTY'"
    )
    
    related_entity_id = models.IntegerField(null=True, blank=True)
    
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_transactions',
        limit_choices_to={'role': 'ADMIN'}
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'finance_transactions'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['transaction_type', 'date']),
            models.Index(fields=['related_user', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type}: {self.amount} - {self.date}"


class UserPoints(models.Model):
    """
    Track user points balance and lifetime statistics.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='points_balance',
        limit_choices_to={'role': 'FIELD_AGENT'}
    )
    
    total_points = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Current total points balance"
    )
    
    available_points = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Points available for redemption"
    )
    
    lifetime_points = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total points earned lifetime"
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_points'
        ordering = ['-total_points']
        indexes = [
            models.Index(fields=['total_points']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"Points: {self.user.work_id} - {self.total_points} available"
    
    def add_points(self, points, transaction_type='EARNED'):
        """Add points to user balance."""
        if points > 0:
            self.total_points += points
            self.available_points += points
            if transaction_type == 'EARNED':
                self.lifetime_points += points
            self.save(update_fields=['total_points', 'available_points', 'lifetime_points', 'updated_at'])
    
    def deduct_points(self, points):
        """Deduct points from user balance."""
        if points > 0:
            self.total_points = max(0, self.total_points - points)
            self.available_points = max(0, self.available_points - points)
            self.save(update_fields=['total_points', 'available_points', 'updated_at'])


class PointsTransaction(models.Model):
    """
    Track all points transactions (earned/deducted/redeemed).
    """
    TRANSACTION_TYPE_CHOICES = [
        ('EARNED', 'Earned'),
        ('DEDUCTED', 'Deducted'),
        ('REDEEMED', 'Redeemed'),
    ]
    
    ACTIVITY_TYPE_CHOICES = [
        ('VISIT_COMPLETION', 'Visit Completion'),
        ('PERFECT_VISIT', 'Perfect Visit'),
        ('IMAGE_QUALITY_BONUS', 'Image Quality Bonus'),
        ('IMAGE_REJECTION_PENALTY', 'Image Rejection Penalty'),
        ('MISSED_VISIT_PENALTY', 'Missed Visit Penalty'),
        ('HIGH_PRIORITY_MISSED', 'High Priority Store Missed'),
        ('REWARD_REDEMPTION', 'Reward Redemption'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='points_transactions',
        limit_choices_to={'role': 'FIELD_AGENT'}
    )
    
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        db_index=True
    )
    
    activity_type = models.CharField(
        max_length=50,
        choices=ACTIVITY_TYPE_CHOICES,
        db_index=True,
        help_text="Type of activity that generated this transaction"
    )
    
    points = models.IntegerField(
        help_text="Points amount (positive for earned, negative for deducted)"
    )
    
    description = models.TextField(null=True, blank=True)
    
    # Related entities
    store_visit = models.ForeignKey(
        'operations.StoreVisit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='points_transactions'
    )
    
    store = models.ForeignKey(
        'core.Store',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='points_transactions'
    )
    
    route = models.ForeignKey(
        'core.Route',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='points_transactions'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'points_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['transaction_type', 'created_at']),
            models.Index(fields=['activity_type', 'created_at']),
            models.Index(fields=['store_visit']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type}: {self.user.work_id} - {self.points} points - {self.activity_type}"
