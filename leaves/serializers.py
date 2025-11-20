from django.utils import timezone
from rest_framework import serializers

from core.models import FileManager
from core.serializers import FileManagerSerializer
from users.serializers import UserSerializer

from .models import LeaveRequest


class LeaveRequestSerializer(serializers.ModelSerializer):
    requested_by = UserSerializer(read_only=True)
    approver = UserSerializer(read_only=True)
    document = FileManagerSerializer(read_only=True)
    leave_type_display = serializers.CharField(source="get_leave_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "requested_by",
            "leave_type",
            "leave_type_display",
            "start_date",
            "end_date",
            "description",
            "document",
            "status",
            "status_display",
            "approver",
            "reviewed_at",
            "reviewer_note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "requested_by",
            "status",
            "status_display",
            "approver",
            "reviewed_at",
            "reviewer_note",
            "created_at",
            "updated_at",
        ]


class LeaveRequestCreateSerializer(serializers.ModelSerializer):
    document = serializers.PrimaryKeyRelatedField(
        queryset=FileManager.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = LeaveRequest
        fields = [
            "leave_type",
            "start_date",
            "end_date",
            "description",
            "document",
        ]

    def validate_leave_type(self, value):
        """Normalize leave_type to handle case-insensitive input and common variations."""
        if not value:
            return value
        
        # Normalize to uppercase and handle common variations
        value_upper = value.upper().strip()
        
        # Map common variations to valid choices
        leave_type_mapping = {
            'SICK': LeaveRequest.LeaveType.SICK,
            'SICK LEAVE': LeaveRequest.LeaveType.SICK,
            'CASUAL': LeaveRequest.LeaveType.CASUAL,
            'CASUAL LEAVE': LeaveRequest.LeaveType.CASUAL,
            'CAUSAL': LeaveRequest.LeaveType.CASUAL,  # Handle typo
            'CAUSAL LEAVE': LeaveRequest.LeaveType.CASUAL,  # Handle typo
        }
        
        # Try exact match first
        if value_upper in leave_type_mapping:
            return leave_type_mapping[value_upper]
        
        # Try to find partial match
        for key, mapped_value in leave_type_mapping.items():
            if value_upper in key or key in value_upper:
                return mapped_value
        
        # If no match found, raise validation error with helpful message
        valid_choices = [choice[0] for choice in LeaveRequest.LeaveType.choices]
        raise serializers.ValidationError(
            f'Invalid leave type. Valid choices are: {", ".join(valid_choices)} '
            f'(or their display names: {", ".join([choice[1] for choice in LeaveRequest.LeaveType.choices])})'
        )

    def validate(self, attrs):
        start = attrs.get("start_date")
        end = attrs.get("end_date")
        if start and end and start > end:
            raise serializers.ValidationError({"end_date": "End date must be on or after start date."})

        document = attrs.get("document")
        user = self.context["request"].user
        if document and document.user != user and user.role not in ("MANAGER", "ADMIN"):
            raise serializers.ValidationError({"document": "You can only attach documents you uploaded."})
        return attrs

    def create(self, validated_data):
        return LeaveRequest.objects.create(
            requested_by=self.context["request"].user,
            **validated_data,
        )


class LeaveRequestStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ["status", "reviewer_note"]

    def validate_status(self, value):
        if value not in [LeaveRequest.Status.APPROVED, LeaveRequest.Status.REJECTED, LeaveRequest.Status.CANCELLED]:
            raise serializers.ValidationError("Status must be APPROVED, REJECTED, or CANCELLED.")
        return value

    def update(self, instance, validated_data):
        instance.status = validated_data["status"]
        instance.reviewer_note = validated_data.get("reviewer_note", instance.reviewer_note)
        instance.approver = self.context["request"].user
        instance.reviewed_at = timezone.now()
        instance.save(update_fields=["status", "reviewer_note", "approver", "reviewed_at", "updated_at"])
        return instance


class LeaveRequestCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ["status"]

    def validate(self, attrs):
        if self.instance.status != LeaveRequest.Status.PENDING:
            raise serializers.ValidationError("Only pending requests can be cancelled.")
        return attrs

    def update(self, instance, validated_data):
        instance.status = LeaveRequest.Status.CANCELLED
        instance.reviewed_at = timezone.now()
        instance.approver = self.context["request"].user
        instance.save(update_fields=["status", "reviewed_at", "approver", "updated_at"])
        return instance

