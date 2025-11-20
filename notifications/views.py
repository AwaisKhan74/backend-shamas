from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from notifications.models import Notification
from notifications.serializers import NotificationSerializer, NotificationListSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing user notifications.
    
    Endpoints:
    - GET /api/notifications/ - List all notifications (paginated)
    - GET /api/notifications/{id}/ - Get notification details
    - POST /api/notifications/{id}/mark_read/ - Mark a notification as read
    - POST /api/notifications/mark_all_read/ - Mark all notifications as read
    - GET /api/notifications/unread_count/ - Get count of unread notifications
    - DELETE /api/notifications/clear_all/ - Delete all read notifications
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return notifications for the current user."""
        queryset = Notification.objects.filter(user=self.request.user)
        
        # Filter by read status if provided
        is_read = self.request.query_params.get('is_read', None)
        if is_read is not None:
            is_read_bool = is_read.lower() == 'true'
            queryset = queryset.filter(is_read=is_read_bool)
        
        # Filter by notification type if provided
        notification_type = self.request.query_params.get('type', None)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NotificationListSerializer
        return NotificationSerializer
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read."""
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response({
            'success': True,
            'message': 'Notification marked as read.',
            'notification': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        count = self.get_queryset().filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({
            'success': True,
            'message': f'{count} notifications marked as read.',
            'count': count
        })
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})
    
    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """Delete all read notifications."""
        count, _ = self.get_queryset().filter(is_read=True).delete()
        return Response({
            'success': True,
            'message': f'{count} notifications deleted.',
            'count': count
        })
