"""
Serializers for core operational models.
"""
from rest_framework import serializers

from users.models import User
from users.serializers import UserSerializer
from .models import Counter, District, FileManager, Route, RouteStore, Store


class CounterSerializer(serializers.ModelSerializer):
    """
    Serializer for Counter model.
    Uses User's is_active field from AbstractUser.
    """
    user_detail = UserSerializer(source='user', read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='FIELD_AGENT'),
        write_only=True,
        required=False
    )
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Counter
        fields = [
            'id', 'user', 'user_detail', 'employee_id', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_active', 'created_at', 'updated_at']
    
    def get_is_active(self, obj):
        """Get is_active from the related User model."""
        return obj.user.is_active if obj.user else False
    
    def validate_employee_id(self, value):
        """Validate employee_id is unique."""
        if self.instance and self.instance.employee_id == value:
            return value
        
        if Counter.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError(
                "A counter with this employee ID already exists."
            )
        return value


class DistrictListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for district lists.
    """
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    stores_count = serializers.SerializerMethodField()
    
    class Meta:
        model = District
        fields = [
            'id', 'name', 'code', 'priority', 'priority_display',
            'status', 'stores_count'
        ]
    
    def get_stores_count(self, obj):
        return obj.stores.filter(status='ACTIVE').count()


class DistrictSerializer(serializers.ModelSerializer):
    """
    Serializer for District model.
    """
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    stores_count = serializers.SerializerMethodField()
    
    class Meta:
        model = District
        fields = [
            'id', 'name', 'code', 'priority', 'priority_display',
            'status', 'status_display', 'description',
            'stores_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_stores_count(self, obj):
        """Return count of active stores in this district."""
        return obj.stores.filter(status='ACTIVE').count()


class DistrictStatsSerializer(serializers.ModelSerializer):
    """
    Serializer for district with today's route statistics.
    Used for "Today's Districts" API.
    """
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    stores_assigned = serializers.SerializerMethodField()
    stores_visited = serializers.SerializerMethodField()
    stores_pending = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = District
        fields = [
            'id', 'name', 'code', 'priority', 'priority_display',
            'stores_assigned', 'stores_visited', 'stores_pending',
            'progress_percentage'
        ]
    
    def get_stores_assigned(self, obj):
        """Count stores assigned in today's routes for this district."""
        from django.utils import timezone
        from core.models import RouteStore
        
        today = timezone.localdate()
        routes_today = obj.routes.filter(date=today, status__in=['APPROVED', 'STARTED', 'COMPLETED'])
        route_ids = routes_today.values_list('id', flat=True)
        return RouteStore.objects.filter(route_id__in=route_ids).count()
    
    def get_stores_visited(self, obj):
        """Count stores visited in today's routes for this district."""
        from django.utils import timezone
        from operations.models import StoreVisit
        
        today = timezone.localdate()
        routes_today = obj.routes.filter(date=today)
        route_ids = routes_today.values_list('id', flat=True)
        return StoreVisit.objects.filter(
            route_id__in=route_ids,
            status='COMPLETED'
        ).count()
    
    def get_stores_pending(self, obj):
        """Calculate pending stores."""
        assigned = self.get_stores_assigned(obj)
        visited = self.get_stores_visited(obj)
        return max(0, assigned - visited)
    
    def get_progress_percentage(self, obj):
        """Calculate progress percentage."""
        assigned = self.get_stores_assigned(obj)
        if assigned == 0:
            return 0
        visited = self.get_stores_visited(obj)
        return round((visited / assigned) * 100, 1)


class StoreSerializer(serializers.ModelSerializer):
    """
    Serializer for Store model.
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    district_detail = DistrictListSerializer(source='district', read_only=True)
    district = serializers.PrimaryKeyRelatedField(
        queryset=District.objects.filter(status='ACTIVE'),
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Store
        fields = [
            'id', 'name', 'address', 'district', 'district_detail',
            'latitude', 'longitude', 'contact_person', 'phone_number',
            'status', 'status_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """Validate GPS coordinates if provided."""
        latitude = attrs.get('latitude')
        longitude = attrs.get('longitude')
        
        # If one coordinate is provided, both should be provided
        if (latitude is not None and longitude is None) or \
           (latitude is None and longitude is not None):
            raise serializers.ValidationError({
                'error': 'Both latitude and longitude must be provided together.'
            })
        
        return attrs


class RouteStoreSerializer(serializers.ModelSerializer):
    """
    Serializer for RouteStore model (nested).
    """
    store_detail = StoreSerializer(source='store', read_only=True)
    store = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(),
        write_only=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = RouteStore
        fields = [
            'id', 'route', 'store', 'store_detail', 'order',
            'status', 'status_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'route', 'created_at', 'updated_at']


class RouteSerializer(serializers.ModelSerializer):
    """
    Serializer for Route model.
    """
    user_detail = UserSerializer(source='user', read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='FIELD_AGENT'),
        write_only=True
    )
    approved_by_detail = UserSerializer(source='approved_by', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    district_detail = DistrictListSerializer(source='district', read_only=True)
    district = serializers.PrimaryKeyRelatedField(
        queryset=District.objects.filter(status='ACTIVE'),
        write_only=True,
        required=False,
        allow_null=True
    )
    route_stores = RouteStoreSerializer(many=True, read_only=True)
    stores = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Store.objects.all(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Route
        fields = [
            'id', 'name', 'description', 'district', 'district_detail',
            'user', 'user_detail', 'date', 'status', 'status_display',
            'start_time', 'end_time', 'approved_by', 'approved_by_detail',
            'approved_at', 'route_stores', 'stores', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'approved_by', 'approved_at', 'created_at', 'updated_at'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set queryset for user field to only field agents
        if self.fields.get('user'):
            from users.models import User
            self.fields['user'].queryset = User.objects.filter(role='FIELD_AGENT')
    
    def create(self, validated_data):
        """Create route with stores."""
        stores = validated_data.pop('stores', [])
        route = Route.objects.create(**validated_data)
        
        # Create RouteStore entries with order
        for index, store in enumerate(stores, start=1):
            RouteStore.objects.create(
                route=route,
                store=store,
                order=index
            )
        
        return route
    
    def update(self, instance, validated_data):
        """Update route and optionally update stores."""
        stores = validated_data.pop('stores', None)
        
        # Update route fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update stores if provided
        if stores is not None:
            # Delete existing route stores
            instance.route_stores.all().delete()
            
            # Create new route stores
            for index, store in enumerate(stores, start=1):
                RouteStore.objects.create(
                    route=instance,
                    store=store,
                    order=index
                )
        
        return instance


class RouteListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for route listing (optimized for performance).
    """
    user_detail = serializers.SerializerMethodField()
    approved_by_detail = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    stores_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Route
        fields = [
            'id', 'name', 'description', 'user_detail', 'date',
            'status', 'status_display', 'start_time', 'end_time',
            'approved_by_detail', 'stores_count', 'created_at'
        ]
    
    def get_user_detail(self, obj):
        """Get minimal user info."""
        return {
            'id': obj.user.id,
            'work_id': obj.user.work_id,
            'full_name': obj.user.get_full_name() or obj.user.username
        }
    
    def get_approved_by_detail(self, obj):
        """Get minimal approved by info."""
        if obj.approved_by:
            return {
                'id': obj.approved_by.id,
                'work_id': obj.approved_by.work_id,
                'full_name': obj.approved_by.get_full_name() or obj.approved_by.username
            }
        return None
    
    def get_stores_count(self, obj):
        """Get count of stores in route."""
        return obj.route_stores.count()


class FileManagerSerializer(serializers.ModelSerializer):
    """
    Serializer for FileManager model - centralized file/image management.
    """
    user_detail = UserSerializer(source='user', read_only=True)
    route_detail = serializers.SerializerMethodField()
    file_type_display = serializers.CharField(source='get_file_type_display', read_only=True)
    purpose_display = serializers.CharField(source='get_purpose_display', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = FileManager
        fields = [
            'id', 'user', 'user_detail', 'route', 'route_detail',
            'file', 'file_url', 'file_type', 'file_type_display',
            'purpose', 'purpose_display', 'description',
            'file_name', 'file_size', 'file_size_mb',
            'bucket', 'object_key', 'content_type', 'checksum',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'file_size', 'bucket', 'object_key',
            'content_type', 'checksum', 'created_at', 'updated_at'
        ]
    
    def get_route_detail(self, obj):
        """Get minimal route info if route exists."""
        if obj.route:
            return {
                'id': obj.route.id,
                'name': obj.route.name,
                'date': obj.route.date
            }
        return None
    
    def get_file_url(self, obj):
        """Get file URL."""
        return obj.file_url
    
    def get_file_size_mb(self, obj):
        """Get file size in MB."""
        return obj.file_size_mb


class FileManagerUploadSerializer(serializers.ModelSerializer):
    """
    Serializer used for handling file uploads.
    """

    class Meta:
        model = FileManager
        fields = [
            'file',
            'file_type',
            'purpose',
            'route',
            'description',
            'is_active',
        ]
        extra_kwargs = {
            'is_active': {'required': False},
            'description': {'required': False, 'allow_blank': True},
            'file_type': {'required': False},
            'purpose': {'required': False},
        }

    def create(self, validated_data):
        validated_data.setdefault('user', self.context['request'].user)
        return super().create(validated_data)


class FileManagerListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for FileManager list views.
    """
    user_detail = serializers.SerializerMethodField()
    route_detail = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = FileManager
        fields = [
            'id', 'user_detail', 'route_detail', 'file_url',
            'file_type', 'purpose', 'file_name',
            'file_size_mb', 'is_active', 'created_at'
        ]
    
    def get_user_detail(self, obj):
        """Get minimal user info."""
        return {
            'id': obj.user.id,
            'work_id': obj.user.work_id,
            'full_name': obj.user.get_full_name() or obj.user.username
        }
    
    def get_route_detail(self, obj):
        """Get minimal route info."""
        if obj.route:
            return {
                'id': obj.route.id,
                'name': obj.route.name,
                'date': obj.route.date
            }
        return None
    
    def get_file_url(self, obj):
        """Get file URL."""
        return obj.file_url
    
    def get_file_size_mb(self, obj):
        """Get file size in MB."""
        return obj.file_size_mb

