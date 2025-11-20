from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.permissions import IsManagerOrAdmin

from .models import LeaveRequest
from .serializers import (
    LeaveRequestCancelSerializer,
    LeaveRequestCreateSerializer,
    LeaveRequestSerializer,
    LeaveRequestStatusUpdateSerializer,
)


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """
    Manage leave requests for employees and approvers.
    """

    queryset = LeaveRequest.objects.select_related(
        "requested_by",
        "approver",
        "document",
    )
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ("MANAGER", "ADMIN"):
            return self.queryset
        return self.queryset.filter(requested_by=user)

    def get_serializer_class(self):
        if self.action == "create":
            return LeaveRequestCreateSerializer
        if self.action in ("update", "partial_update"):
            return LeaveRequestCreateSerializer
        if self.action == "set_status":
            return LeaveRequestStatusUpdateSerializer
        if self.action == "cancel":
            return LeaveRequestCancelSerializer
        return LeaveRequestSerializer

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.updated_at = timezone.now()
        instance.save(update_fields=["updated_at"])

    def perform_destroy(self, instance):
        if self.request.user != instance.requested_by and self.request.user.role not in ("MANAGER", "ADMIN"):
            raise permissions.PermissionDenied("You can only delete your own leave requests.")
        super().perform_destroy(instance)

    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[permissions.IsAuthenticated, IsManagerOrAdmin],
        url_path="status",
    )
    def set_status(self, request, pk=None):
        leave_request = self.get_object()
        serializer = self.get_serializer(leave_request, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(LeaveRequestSerializer(leave_request, context=self.get_serializer_context()).data)

    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def cancel(self, request, pk=None):
        leave_request = self.get_object()
        if leave_request.requested_by != request.user and request.user.role not in ("MANAGER", "ADMIN"):
            raise permissions.PermissionDenied("You do not have permission to cancel this request.")
        serializer = self.get_serializer(leave_request, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(LeaveRequestSerializer(leave_request, context=self.get_serializer_context()).data, status=status.HTTP_200_OK)

