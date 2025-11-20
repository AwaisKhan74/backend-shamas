"""
Serializers for administration app (penalties, daily summaries).
"""
from rest_framework import serializers
from users.serializers import UserSerializer
from core.serializers import StoreSerializer
from .models import Penalty


class PenaltySerializer(serializers.ModelSerializer):
    """Serializer for Penalty model."""
    user_detail = UserSerializer(source='user', read_only=True)
    store_detail = serializers.SerializerMethodField()
    penalty_type_display = serializers.CharField(source='get_penalty_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    issued_by_detail = UserSerializer(source='issued_by', read_only=True)
    
    class Meta:
        model = Penalty
        fields = [
            'id', 'user', 'user_detail',
            'route', 'store', 'store_detail',
            'reason', 'amount', 'points_deducted',
            'penalty_type', 'penalty_type_display',
            'status', 'status_display',
            'store_visit',
            'issued_by', 'issued_by_detail',
            'issued_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'issued_at', 'created_at', 'updated_at']
    
    def get_store_detail(self, obj):
        """Get minimal store info."""
        if obj.store:
            return {
                'id': obj.store.id,
                'name': obj.store.name,
                'district': obj.store.district.name if obj.store.district else None,
                'priority': obj.store.priority,
                'priority_display': obj.store.get_priority_display()
            }
        return None


class PenaltyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for penalty list with summary."""
    store_name = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    
    class Meta:
        model = Penalty
        fields = [
            'id', 'store_name', 'district_name',
            'amount', 'points_deducted', 'reason',
            'status', 'date', 'issued_at'
        ]
        read_only_fields = ['id', 'issued_at']
    
    def get_store_name(self, obj):
        """Get store name."""
        return obj.store.name if obj.store else None
    
    def get_district_name(self, obj):
        """Get district name."""
        if obj.store and obj.store.district:
            return obj.store.district.name
        return None
    
    def get_date(self, obj):
        """Get formatted date."""
        return obj.issued_at.strftime('%b %d') if obj.issued_at else None

