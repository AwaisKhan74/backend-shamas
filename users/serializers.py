"""
Serializers for user authentication and management.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for returning user information alongside profile data."""

    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    profile_image = serializers.SerializerMethodField()
    location_access_enabled = serializers.BooleanField(source='has_gps_permission', read_only=True)
    camera_access_enabled = serializers.BooleanField(source='has_camera_permission', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'work_id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'display_name', 'phone_number', 'role', 'role_display',
            'status', 'profile_image',
            'has_gps_permission', 'has_camera_permission',
            'location_access_enabled', 'camera_access_enabled',
            'push_notifications_enabled', 'route_reminders_enabled',
            'reward_alerts_enabled', 'qc_alerts_enabled',
            'preferred_language',
            'country', 'city', 'address',
            'is_active', 'date_joined', 'last_login', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'created_at', 'updated_at',
            'is_active'
        ]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_profile_image(self, obj):
        if not obj.profile_picture:
            return None
        request = self.context.get('request') if hasattr(self, 'context') else None
        url = obj.profile_picture.url
        if request:
            return request.build_absolute_uri(url)
        return url


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users (registration).
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    class Meta:
        model = User
        fields = [
            'work_id', 'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number', 'display_name',
            'status', 'country', 'city', 'address', 'role',
            'has_gps_permission', 'has_camera_permission',
            'push_notifications_enabled', 'route_reminders_enabled',
            'reward_alerts_enabled', 'qc_alerts_enabled',
            'preferred_language'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'work_id': {'required': True},
            'role': {'required': True},
            'status': {'required': False},
            'display_name': {'required': False, 'allow_blank': True},
            'country': {'required': False, 'allow_blank': True},
            'city': {'required': False, 'allow_blank': True},
            'address': {'required': False, 'allow_blank': True},
            'phone_number': {'required': False, 'allow_blank': True, 'allow_null': True},
            'has_gps_permission': {'required': False},
            'has_camera_permission': {'required': False},
            'push_notifications_enabled': {'required': False},
            'route_reminders_enabled': {'required': False},
            'reward_alerts_enabled': {'required': False},
            'qc_alerts_enabled': {'required': False},
            'preferred_language': {'required': False},
        }
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Passwords don't match."
            })
        return attrs
    
    def validate_work_id(self, value):
        """Validate work_id is unique."""
        if User.objects.filter(work_id=value).exists():
            raise serializers.ValidationError("A user with this work ID already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate_email(self, value):
        """Validate email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone_number(self, value):
        if not value:
            return value
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value
    
    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """Validate old password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "New passwords don't match."
            })
        return attrs
    
    def save(self):
        """Update user password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    work_id = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate credentials."""
        work_id = attrs.get('work_id')
        email = attrs.get('email')
        password = attrs.get('password')
        
        if not (work_id or email):
            raise serializers.ValidationError({
                'error': 'Either work_id or email is required.'
            })
        
        # Find user by work_id or email
        try:
            if work_id:
                user = User.objects.get(work_id=work_id)
            else:
                user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'error': 'Invalid credentials.'
            })
        
        # Authenticate user
        if not user.check_password(password):
            raise serializers.ValidationError({
                'error': 'Invalid credentials.'
            })
        
        if not user.is_active:
            raise serializers.ValidationError({
                'error': 'User account is disabled.'
            })
        
        attrs['user'] = user
        return attrs


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile fields directly on the User model."""

    location_access_enabled = serializers.BooleanField(
        source='has_gps_permission', required=False
    )
    camera_access_enabled = serializers.BooleanField(
        source='has_camera_permission', required=False
    )

    class Meta:
        model = User
        fields = [
            'display_name', 'status', 'country', 'city', 'address',
            'first_name', 'last_name', 'phone_number',
            'profile_picture', 'has_gps_permission', 'has_camera_permission',
            'location_access_enabled', 'camera_access_enabled',
            'push_notifications_enabled', 'route_reminders_enabled',
            'reward_alerts_enabled', 'qc_alerts_enabled',
            'preferred_language'
        ]
        extra_kwargs = {
            'status': {'required': False},
            'display_name': {'required': False, 'allow_blank': True},
            'country': {'required': False, 'allow_blank': True},
            'city': {'required': False, 'allow_blank': True},
            'address': {'required': False, 'allow_blank': True},
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'phone_number': {'required': False, 'allow_blank': True, 'allow_null': True},
            'profile_picture': {'required': False, 'allow_null': True},
            'has_gps_permission': {'required': False},
            'has_camera_permission': {'required': False},
            'push_notifications_enabled': {'required': False},
            'route_reminders_enabled': {'required': False},
            'reward_alerts_enabled': {'required': False},
            'qc_alerts_enabled': {'required': False},
            'preferred_language': {'required': False},
        }

    def validate_phone_number(self, value):
        if not value:
            return value
        user = self.instance
        if User.objects.filter(phone_number=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for administrators updating other users."""

    location_access_enabled = serializers.BooleanField(
        source='has_gps_permission', required=False
    )
    camera_access_enabled = serializers.BooleanField(
        source='has_camera_permission', required=False
    )

    class Meta:
        model = User
        fields = [
            'work_id', 'username', 'email',
            'first_name', 'last_name', 'display_name',
            'status', 'role',
            'phone_number', 'country', 'city', 'address',
            'has_gps_permission', 'has_camera_permission',
            'location_access_enabled', 'camera_access_enabled',
            'push_notifications_enabled', 'route_reminders_enabled',
            'reward_alerts_enabled', 'qc_alerts_enabled',
            'preferred_language',
            'is_active', 'profile_picture'
        ]
        extra_kwargs = {
            'work_id': {'required': False, 'allow_blank': False},
            'username': {'required': False, 'allow_blank': False},
            'email': {'required': False},
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'display_name': {'required': False, 'allow_blank': True},
            'status': {'required': False},
            'role': {'required': False},
            'phone_number': {'required': False, 'allow_blank': True, 'allow_null': True},
            'country': {'required': False, 'allow_blank': True},
            'city': {'required': False, 'allow_blank': True},
            'address': {'required': False, 'allow_blank': True},
            'has_gps_permission': {'required': False},
            'has_camera_permission': {'required': False},
            'push_notifications_enabled': {'required': False},
            'route_reminders_enabled': {'required': False},
            'reward_alerts_enabled': {'required': False},
            'qc_alerts_enabled': {'required': False},
            'preferred_language': {'required': False},
            'is_active': {'required': False},
            'profile_picture': {'required': False, 'allow_null': True},
        }

    def validate_work_id(self, value):
        if not value:
            return value
        if User.objects.filter(work_id=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("A user with this work ID already exists.")
        return value

    def validate_username(self, value):
        if not value:
            return value
        if User.objects.filter(username=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_email(self, value):
        if not value:
            return value
        if User.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone_number(self, value):
        if not value:
            return value
        if User.objects.filter(phone_number=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting password reset.
    """
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    
    def validate(self, attrs):
        """Validate that at least one identifier is provided."""
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')
        
        if not (email or phone_number):
            raise serializers.ValidationError({
                'error': 'Either email or phone_number is required.'
            })
        
        try:
            if email:
                user = User.objects.get(email=email)
            else:
                user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            # Don't reveal if user exists or not (security best practice)
            pass
        
        return attrs


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming password reset with token.
    """
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "Passwords don't match."
            })
        return attrs

