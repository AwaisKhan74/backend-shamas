"""
Serializers for finance app (rewards, points, transactions).
"""
from rest_framework import serializers
from users.serializers import UserSerializer
from core.serializers import StoreSerializer
from .models import Reward, UserReward, UserPoints, PointsTransaction


class RewardSerializer(serializers.ModelSerializer):
    """Serializer for Reward model."""
    
    class Meta:
        model = Reward
        fields = [
            'id', 'name', 'description', 'points_required',
            'value', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserPointsSerializer(serializers.ModelSerializer):
    """Serializer for UserPoints model."""
    user_detail = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = UserPoints
        fields = [
            'id', 'user', 'user_detail',
            'total_points', 'available_points', 'lifetime_points',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PointsTransactionSerializer(serializers.ModelSerializer):
    """Serializer for PointsTransaction model."""
    user_detail = UserSerializer(source='user', read_only=True)
    store_detail = serializers.SerializerMethodField()
    activity_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = PointsTransaction
        fields = [
            'id', 'user', 'user_detail',
            'transaction_type', 'transaction_type_display',
            'activity_type', 'activity_display',
            'points', 'description',
            'store_visit', 'store', 'store_detail', 'route',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_store_detail(self, obj):
        """Get minimal store info."""
        if obj.store:
            return {
                'id': obj.store.id,
                'name': obj.store.name,
                'district': obj.store.district.name if obj.store.district else None
            }
        return None


class RewardActivitySerializer(serializers.ModelSerializer):
    """Serializer for reward activity display (used in rewards activity list)."""
    activity_display = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    
    class Meta:
        model = PointsTransaction
        fields = [
            'id', 'activity_type', 'activity_display',
            'points', 'store_name', 'district_name',
            'status', 'date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_activity_display(self, obj):
        """Get human-readable activity type."""
        activity_map = {
            'VISIT_COMPLETION': 'Visit Completion',
            'PERFECT_VISIT': 'Perfect Visit',
            'IMAGE_QUALITY_BONUS': 'Image Quality Bonus',
            'IMAGE_REJECTION_PENALTY': 'Image Rejection Penalty',
            'MISSED_VISIT_PENALTY': 'Missed Visit Penalty',
            'HIGH_PRIORITY_MISSED': 'High Priority Store Missed',
            'REWARD_REDEMPTION': 'Reward Redemption',
        }
        return activity_map.get(obj.activity_type, obj.activity_type)
    
    def get_store_name(self, obj):
        """Get store name."""
        return obj.store.name if obj.store else None
    
    def get_district_name(self, obj):
        """Get district name."""
        if obj.store and obj.store.district:
            return obj.store.district.name
        return None
    
    def get_status(self, obj):
        """Get status (always 'APPROVED' for earned points)."""
        if obj.transaction_type == 'EARNED':
            return 'APPROVED'
        return 'DEDUCTED'
    
    def get_date(self, obj):
        """Get formatted date."""
        return obj.created_at.strftime('%b %d/%Y') if obj.created_at else None


class UserRewardSerializer(serializers.ModelSerializer):
    """Serializer for UserReward model."""
    user_detail = UserSerializer(source='user', read_only=True)
    reward_detail = RewardSerializer(source='reward', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = UserReward
        fields = [
            'id', 'user', 'user_detail',
            'reward', 'reward_detail',
            'amount', 'description',
            'activity_type', 'points_earned',
            'store_visit',
            'status', 'status_display',
            'earned_at', 'awarded_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'earned_at', 'created_at', 'updated_at']

