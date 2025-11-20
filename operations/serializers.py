"""
Serializers for field agent operations.
"""
from rest_framework import serializers

from core.models import Route, Store
from core.serializers import StoreSerializer
from users.serializers import UserSerializer

from .models import Break, CheckIn, FlaggedStore, Image, PermissionForm, StoreVisit


class CheckInSerializer(serializers.ModelSerializer):
    """
    Serializer for CheckIn model representing a work session.
    """
    user_detail = UserSerializer(source='user', read_only=True)
    total_break_seconds = serializers.SerializerMethodField()
    total_hours_worked = serializers.SerializerMethodField()
    total_hours_worked_seconds = serializers.SerializerMethodField()
    break_duration_hours = serializers.SerializerMethodField()
    break_duration_seconds = serializers.SerializerMethodField()
    remaining_shift_hours = serializers.SerializerMethodField()
    remaining_shift_seconds = serializers.SerializerMethodField()

    class Meta:
        model = CheckIn
        fields = [
            'id',
            'user',
            'user_detail',
            'shift_date',
            'timestamp',
            'latitude',
            'longitude',
            'check_out_time',
            'check_out_latitude',
            'check_out_longitude',
            'status',
            'current_break_start',
            'total_break_duration',
            'total_break_seconds',
            'total_hours_worked',
            'total_hours_worked_seconds',
            'break_duration_hours',
            'break_duration_seconds',
            'remaining_shift_hours',
            'remaining_shift_seconds',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'shift_date',
            'check_out_time',
            'check_out_latitude',
            'check_out_longitude',
            'status',
            'current_break_start',
            'total_break_duration',
            'total_break_seconds',
            'total_hours_worked',
            'total_hours_worked_seconds',
            'break_duration_hours',
            'break_duration_seconds',
            'remaining_shift_hours',
            'remaining_shift_seconds',
            'created_at',
            'updated_at',
        ]

    def validate(self, attrs):
        """Validate GPS coordinates."""
        latitude = attrs.get('latitude')
        longitude = attrs.get('longitude')

        if latitude is None or longitude is None:
            raise serializers.ValidationError({
                'error': 'Both latitude and longitude are required.'
            })

        return attrs

    def get_total_break_seconds(self, obj):
        if obj.total_break_duration is not None:
            return int(obj.total_break_duration.total_seconds())
        return 0
    
    def get_total_hours_worked(self, obj):
        """Get total hours worked (excluding breaks)."""
        return round(obj.total_hours_worked, 2)
    
    def get_total_hours_worked_seconds(self, obj):
        """Get total hours worked in seconds."""
        return obj.total_hours_worked_seconds
    
    def get_break_duration_hours(self, obj):
        """Get break duration in hours."""
        return round(obj.break_duration_hours, 2)
    
    def get_break_duration_seconds(self, obj):
        """Get break duration in seconds."""
        return obj.break_duration_seconds
    
    def get_remaining_shift_hours(self, obj):
        """Get remaining shift hours (9 hours total)."""
        return round(obj.remaining_shift_hours, 2)
    
    def get_remaining_shift_seconds(self, obj):
        """Get remaining shift time in seconds."""
        return obj.remaining_shift_seconds

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None
        return CheckIn.objects.create(user=user, **validated_data)


class BreakSerializer(serializers.ModelSerializer):
    """
    Serializer for Break model.
    """
    user_detail = UserSerializer(source='user', read_only=True)
    route_detail = serializers.SerializerMethodField()
    duration_seconds = serializers.SerializerMethodField()
    session_id = serializers.IntegerField(source='session.id', read_only=True)

    class Meta:
        model = Break
        fields = [
            'id',
            'session',
            'session_id',
            'user',
            'user_detail',
            'route',
            'route_detail',
            'start_time',
            'end_time',
            'duration',
            'duration_seconds',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'session', 'user', 'duration', 'created_at', 'updated_at']
    
    def get_route_detail(self, obj):
        """Get route details if route exists."""
        if obj.route:
            return {
                'id': obj.route.id,
                'name': obj.route.name,
                'date': str(obj.route.date),
                'status': obj.route.status
            }
        return None

    def get_route_detail(self, obj):
        """Get minimal route info."""
        if not obj.route:
            return None
        return {
            'id': obj.route.id,
            'name': obj.route.name,
            'date': obj.route.date
        }

    def get_duration_seconds(self, obj):
        """Get duration in seconds."""
        if obj.duration:
            return obj.duration.total_seconds()
        return None
    
    def validate(self, attrs):
        """Validate break times."""
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        
        if end_time and start_time and end_time <= start_time:
            raise serializers.ValidationError({
                'end_time': 'End time must be after start time.'
            })
        
        return attrs


class ImageSerializer(serializers.ModelSerializer):
    """
    Serializer for Image model.
    """
    user_detail = UserSerializer(source='user', read_only=True)
    image_type_display = serializers.CharField(source='get_image_type_display', read_only=True)
    
    class Meta:
        model = Image
        fields = [
            'id', 'store_visit', 'user', 'user_detail',
            'image_url', 'captured_at', 'image_type', 'image_type_display',
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'captured_at', 'created_at']


class PermissionFormCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Store Permission Form.
    """
    store_visit = serializers.PrimaryKeyRelatedField(
        queryset=StoreVisit.objects.all(),
        required=True
    )
    
    signature_file = serializers.FileField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text="Signature image file (optional)"
    )
    
    class Meta:
        model = PermissionForm
        fields = [
            'store_visit',
            'representative_name',
            'representative_designation',
            'representative_contact',
            'permission_received',
            'signature_file',
            'permission_granted_confirmed',
            'representative_details_verified',
            'ready_to_begin_collection',
            'is_flagged'
        ]
        read_only_fields = []
    
    def validate(self, attrs):
        """Validate permission form data."""
        permission_received = attrs.get('permission_received')
        representative_name = attrs.get('representative_name')
        representative_designation = attrs.get('representative_designation')
        
        if permission_received is None:
            raise serializers.ValidationError({
                'permission_received': 'Permission received status is required.'
            })
        
        if not representative_name:
            raise serializers.ValidationError({
                'representative_name': 'Representative name is required.'
            })
        
        if not representative_designation:
            raise serializers.ValidationError({
                'representative_designation': 'Representative designation is required.'
            })
        
        # If permission not received, must be flagged
        if not permission_received:
            attrs['is_flagged'] = True
        
        return attrs
    
    def create(self, validated_data):
        """Create permission form and handle signature upload."""
        signature_file = validated_data.pop('signature_file', None)
        store_visit = validated_data['store_visit']
        
        # Create permission form
        permission_form = PermissionForm.objects.create(**validated_data)
        
        # Handle signature upload if provided
        if signature_file:
            from core.models import FileManager
            signature_file_obj = FileManager.objects.create(
                user=self.context['request'].user,
                file=signature_file,
                file_type='IMAGE',
                purpose='PERMISSION_FORM_SIGNATURE',
                description=f"Signature for permission form - {store_visit.store.name}"
            )
            permission_form.signature = signature_file_obj
            permission_form.save(update_fields=['signature'])
        
        # Update store visit status if flagged
        if permission_form.is_flagged:
            store_visit.status = 'FLAGGED'
            store_visit.save(update_fields=['status'])
        
        return permission_form


class PermissionFormSerializer(serializers.ModelSerializer):
    """
    Serializer for reading PermissionForm with details.
    """
    store_visit_detail = serializers.SerializerMethodField()
    signature_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PermissionForm
        fields = [
            'id', 'store_visit', 'store_visit_detail',
            'representative_name', 'representative_designation',
            'representative_contact', 'permission_received',
            'signature', 'signature_url',
            'permission_granted_confirmed',
            'representative_details_verified',
            'ready_to_begin_collection',
            'is_flagged',
            'form_data',
            'submitted_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'submitted_at', 'created_at', 'updated_at']
    
    def get_store_visit_detail(self, obj):
        """Get minimal store visit info."""
        return {
            'id': obj.store_visit.id,
            'store_name': obj.store_visit.store.name,
            'store_address': obj.store_visit.store.address,
            'route_name': obj.store_visit.route.name,
            'route_id': obj.store_visit.route.id,
            'status': obj.store_visit.status
        }
    
    def get_signature_url(self, obj):
        """Get signature file URL."""
        if obj.signature:
            return obj.signature.file_url
        return None


class FlaggedStoreCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating FlaggedStore.
    """
    store_visit = serializers.PrimaryKeyRelatedField(
        queryset=StoreVisit.objects.all(),
        required=True
    )
    
    class Meta:
        model = FlaggedStore
        fields = [
            'store_visit',
            'reason',
            'additional_details'
        ]
    
    def validate(self, attrs):
        """Validate flagged store data."""
        store_visit = attrs['store_visit']
        
        # Check if store visit is already flagged
        if hasattr(store_visit, 'flagged_store'):
            raise serializers.ValidationError({
                'store_visit': 'This store visit is already flagged.'
            })
        
        # Check if permission form exists and is flagged
        if not hasattr(store_visit, 'permission_form'):
            raise serializers.ValidationError({
                'store_visit': 'Permission form must be submitted before flagging.'
            })
        
        if not store_visit.permission_form.is_flagged:
            raise serializers.ValidationError({
                'store_visit': 'Permission form must be flagged before submitting flag reason.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Create flagged store record."""
        validated_data['flagged_by'] = self.context['request'].user
        flagged_store = FlaggedStore.objects.create(**validated_data)
        
        # Update store visit status
        store_visit = flagged_store.store_visit
        store_visit.status = 'FLAGGED'
        store_visit.save(update_fields=['status'])
        
        return flagged_store


class FlaggedStoreSerializer(serializers.ModelSerializer):
    """
    Serializer for reading FlaggedStore with details.
    """
    store_visit_detail = serializers.SerializerMethodField()
    flagged_by_detail = UserSerializer(source='flagged_by', read_only=True)
    resolved_by_detail = UserSerializer(source='resolved_by', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    
    class Meta:
        model = FlaggedStore
        fields = [
            'id', 'store_visit', 'store_visit_detail',
            'reason', 'reason_display',
            'additional_details',
            'flagged_by', 'flagged_by_detail',
            'flagged_at',
            'is_resolved',
            'resolved_by', 'resolved_by_detail',
            'resolved_at', 'resolution_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'flagged_by', 'flagged_at',
            'is_resolved', 'resolved_by', 'resolved_at',
            'created_at', 'updated_at'
        ]
    
    def get_store_visit_detail(self, obj):
        """Get minimal store visit info."""
        return {
            'id': obj.store_visit.id,
            'store_name': obj.store_visit.store.name,
            'store_address': obj.store_visit.store.address,
            'route_name': obj.store_visit.route.name,
            'route_id': obj.store_visit.route.id,
            'visit_date': obj.store_visit.entry_time.date() if obj.store_visit.entry_time else None
        }


class StoreVisitCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating StoreVisit model.
    """
    route = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.all(),
        required=True
    )
    store = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(),
        required=True
    )
    
    class Meta:
        model = StoreVisit
        fields = [
            'route', 'store', 'entry_time', 'exit_time',
            'entry_latitude', 'entry_longitude', 'exit_latitude', 'exit_longitude',
            'status'
        ]
        read_only_fields = []
    
    def validate(self, attrs):
        """Validate GPS coordinates and times."""
        entry_lat = attrs.get('entry_latitude')
        entry_lng = attrs.get('entry_longitude')
        exit_lat = attrs.get('exit_latitude')
        exit_lng = attrs.get('exit_longitude')
        
        # Entry coordinates validation
        if (entry_lat is not None and entry_lng is None) or \
           (entry_lat is None and entry_lng is not None):
            raise serializers.ValidationError({
                'error': 'Both entry latitude and longitude must be provided together.'
            })
        
        # Exit coordinates validation
        if (exit_lat is not None and exit_lng is None) or \
           (exit_lat is None and exit_lng is not None):
            raise serializers.ValidationError({
                'error': 'Both exit latitude and longitude must be provided together.'
            })
        
        # Time validation
        entry_time = attrs.get('entry_time')
        exit_time = attrs.get('exit_time')
        
        if exit_time and entry_time and exit_time <= entry_time:
            raise serializers.ValidationError({
                'exit_time': 'Exit time must be after entry time.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Set user from request context."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
        return super().create(validated_data)


class StoreVisitSerializer(serializers.ModelSerializer):
    """
    Serializer for StoreVisit model.
    """
    user_detail = UserSerializer(source='user', read_only=True)
    store_detail = StoreSerializer(source='store', read_only=True)
    route_detail = serializers.SerializerMethodField()
    approved_by_detail = UserSerializer(source='approved_by', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    ai_ml_check_status_display = serializers.CharField(
        source='get_ai_ml_check_status_display',
        read_only=True
    )
    images = ImageSerializer(many=True, read_only=True)
    permission_form = PermissionFormSerializer(read_only=True)
    
    class Meta:
        model = StoreVisit
        fields = [
            'id', 'user', 'user_detail', 'route', 'route_detail',
            'store', 'store_detail', 'entry_time', 'exit_time',
            'entry_latitude', 'entry_longitude', 'exit_latitude', 'exit_longitude',
            'status', 'status_display', 'submitted_at', 'approved_by', 'approved_by_detail',
            'ai_ml_check_status', 'ai_ml_check_status_display', 'ai_ml_feedback',
            'images', 'permission_form', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'submitted_at', 'approved_by', 'created_at', 'updated_at'
        ]
    
    def get_route_detail(self, obj):
        """Get minimal route info."""
        return {
            'id': obj.route.id,
            'name': obj.route.name,
            'date': obj.route.date
        }
    
    def validate(self, attrs):
        """Validate GPS coordinates and times."""
        entry_lat = attrs.get('entry_latitude')
        entry_lng = attrs.get('entry_longitude')
        exit_lat = attrs.get('exit_latitude')
        exit_lng = attrs.get('exit_longitude')
        
        # Entry coordinates validation
        if (entry_lat is not None and entry_lng is None) or \
           (entry_lat is None and entry_lng is not None):
            raise serializers.ValidationError({
                'error': 'Both entry latitude and longitude must be provided together.'
            })
        
        # Exit coordinates validation
        if (exit_lat is not None and exit_lng is None) or \
           (exit_lat is None and exit_lng is not None):
            raise serializers.ValidationError({
                'error': 'Both exit latitude and longitude must be provided together.'
            })
        
        # Time validation
        entry_time = attrs.get('entry_time')
        exit_time = attrs.get('exit_time')
        
        if exit_time and entry_time and exit_time <= entry_time:
            raise serializers.ValidationError({
                'exit_time': 'Exit time must be after entry time.'
            })
        
        return attrs


class StoreVisitListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for store visit listing.
    """
    store_detail = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    images_count = serializers.SerializerMethodField()
    
    class Meta:
        model = StoreVisit
        fields = [
            'id', 'store_detail', 'entry_time', 'exit_time',
            'status', 'status_display', 'ai_ml_check_status',
            'images_count', 'created_at'
        ]
    
    def get_store_detail(self, obj):
        """Get minimal store info."""
        return {
            'id': obj.store.id,
            'name': obj.store.name,
            'address': obj.store.address[:50] if obj.store.address else None
        }
    
    def get_images_count(self, obj):
        """Get count of images."""
        return obj.images.count()


class StartDaySerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)


class StartBreakSerializer(serializers.Serializer):
    """Serializer for starting a break. Route is optional."""
    route_id = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.all(),
        source='route',
        required=False,
        allow_null=True,
        help_text="Optional route ID. Not required for break tracking."
    )


class CheckOutSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)

