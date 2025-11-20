"""
Notification service for creating and managing notifications.
"""
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from notifications.models import Notification
from users.models import User


class NotificationService:
    """
    Service for creating and managing notifications.
    """
    
    @staticmethod
    def should_send_notification(user, notification_type):
        """
        Check if user has enabled notifications for this type.
        """
        if not user.push_notifications_enabled:
            return False
        
        # Check specific notification preferences
        if notification_type in ['ROUTE_REMINDER', 'STORE_VISIT_REMINDER', 'ROUTE_START_REMINDER']:
            return user.route_reminders_enabled
        elif notification_type in ['REWARD_EARNED', 'POINTS_EARNED', 'POINTS_DEDUCTED']:
            return user.reward_alerts_enabled
        elif notification_type in ['IMAGE_APPROVED', 'IMAGE_REJECTED']:
            return user.qc_alerts_enabled
        
        # Default: send if push notifications are enabled
        return True
    
    @staticmethod
    def create_notification(
        user,
        notification_type,
        title,
        message,
        priority='MEDIUM',
        related_object=None,
        metadata=None
    ):
        """
        Create a notification for a user.
        """
        if not NotificationService.should_send_notification(user, notification_type):
            return None
        
        content_type = None
        object_id = None
        if related_object:
            content_type = ContentType.objects.get_for_model(related_object)
            object_id = related_object.pk
        
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            content_type=content_type,
            object_id=object_id,
            metadata=metadata or {}
        )
        
        return notification
    
    @staticmethod
    def create_leave_notification(leave_request, status):
        """Create notification for leave request status change."""
        user = leave_request.requested_by
        status_map = {
            'APPROVED': {
                'notif_type': 'LEAVE_APPROVED',
                'title': 'Leave Request Approved',
                'message': f'Your leave request from {leave_request.start_date} to {leave_request.end_date} has been approved.',
                'priority': 'MEDIUM'
            },
            'REJECTED': {
                'notif_type': 'LEAVE_REJECTED',
                'title': 'Leave Request Rejected',
                'message': f'Your leave request from {leave_request.start_date} to {leave_request.end_date} has been rejected.',
                'priority': 'HIGH'
            },
            'CANCELLED': {
                'notif_type': 'LEAVE_CANCELLED',
                'title': 'Leave Request Cancelled',
                'message': f'Your leave request from {leave_request.start_date} to {leave_request.end_date} has been cancelled.',
                'priority': 'MEDIUM'
            },
        }
        
        if status in status_map:
            config = status_map[status]
            return NotificationService.create_notification(
                user=user,
                notification_type=config['notif_type'],
                title=config['title'],
                message=config['message'],
                priority=config['priority'],
                related_object=leave_request,
                metadata={
                    'leave_type': leave_request.leave_type,
                    'start_date': str(leave_request.start_date),
                    'end_date': str(leave_request.end_date),
                }
            )
        return None
    
    @staticmethod
    def create_penalty_notification(penalty):
        """Create notification when penalty is issued."""
        penalty_amount = str(penalty.amount) if penalty.amount else None
        points_info = f'{penalty.points_deducted} points' if penalty.points_deducted > 0 else ''
        amount_info = f'{penalty_amount} SAR' if penalty_amount else ''
        
        message_parts = [f'A penalty has been issued for {penalty.penalty_type}.']
        if amount_info:
            message_parts.append(f'Amount: {amount_info}')
        if points_info:
            message_parts.append(f'Points deducted: {points_info}')
        
        return NotificationService.create_notification(
            user=penalty.user,
            notification_type='PENALTY_ISSUED',
            title='Penalty Issued',
            message=' '.join(message_parts),
            priority='HIGH',
            related_object=penalty,
            metadata={
                'penalty_type': penalty.penalty_type,
                'amount': penalty_amount,
                'points_deducted': penalty.points_deducted,
                'reason': penalty.reason[:100] if penalty.reason else None
            }
        )
    
    @staticmethod
    def create_points_notification(user, points, activity_type, description=None):
        """Create notification for points earned/deducted."""
        is_earned = points > 0
        notif_type = 'POINTS_EARNED' if is_earned else 'POINTS_DEDUCTED'
        title = f'{abs(points)} Points {"Earned" if is_earned else "Deducted"}'
        
        message = description or f'{abs(points)} points {"earned" if is_earned else "deducted"} for {activity_type}.'
        
        return NotificationService.create_notification(
            user=user,
            notification_type=notif_type,
            title=title,
            message=message,
            priority='MEDIUM',
            metadata={
                'points': points,
                'activity_type': activity_type,
                'description': description
            }
        )
    
    @staticmethod
    def create_route_notification(route, notification_type='ROUTE_ASSIGNED'):
        """Create notification for route assignment/approval."""
        user = route.user
        title_map = {
            'ROUTE_ASSIGNED': 'New Route Assigned',
            'ROUTE_APPROVED': 'Route Approved',
        }
        
        message_map = {
            'ROUTE_ASSIGNED': f'Route "{route.name}" has been assigned to you for {route.date}.',
            'ROUTE_APPROVED': f'Route "{route.name}" has been approved. You can start your route now.',
        }
        
        return NotificationService.create_notification(
            user=user,
            notification_type=notification_type,
            title=title_map.get(notification_type, 'Route Update'),
            message=message_map.get(notification_type, f'Route "{route.name}" has been updated.'),
            priority='MEDIUM',
            related_object=route,
            metadata={
                'route_name': route.name,
                'route_date': str(route.date),
                'route_status': route.status
            }
        )
    
    @staticmethod
    def create_quality_check_notification(image, status):
        """Create notification for image quality check."""
        user = image.store_visit.user
        store_name = image.store_visit.store.name if image.store_visit.store else 'Store'
        
        status_map = {
            'APPROVED': {
                'notif_type': 'IMAGE_APPROVED',
                'title': 'Image Approved',
                'message': f'Your image from {store_name} has been approved by quality check.',
                'priority': 'MEDIUM'
            },
            'REJECTED': {
                'notif_type': 'IMAGE_REJECTED',
                'title': 'Image Rejected',
                'message': f'Your image from {store_name} has been rejected by quality check.',
                'priority': 'HIGH'
            },
        }
        
        if status in status_map:
            config = status_map[status]
            return NotificationService.create_notification(
                user=user,
                notification_type=config['notif_type'],
                title=config['title'],
                message=config['message'],
                priority=config['priority'],
                related_object=image,
                metadata={
                    'store_name': store_name,
                    'image_type': image.image_type,
                    'quality_status': status
                }
            )
        return None
    
    @staticmethod
    def create_store_visit_notification(store_visit, notification_type):
        """Create notification for store visit events."""
        user = store_visit.user
        store_name = store_visit.store.name if store_visit.store else 'Store'
        
        notification_configs = {
            'STORE_VISIT_COMPLETED': {
                'title': 'Store Visit Completed',
                'message': f'Store visit to {store_name} has been completed successfully.',
                'priority': 'MEDIUM'
            },
            'STORE_VISIT_FLAGGED': {
                'title': 'Store Visit Flagged',
                'message': f'Store visit to {store_name} has been flagged for review.',
                'priority': 'HIGH'
            },
        }
        
        if notification_type in notification_configs:
            config = notification_configs[notification_type]
            return NotificationService.create_notification(
                user=user,
                notification_type=notification_type,
                title=config['title'],
                message=config['message'],
                priority=config['priority'],
                related_object=store_visit,
                metadata={
                    'store_name': store_name,
                    'visit_status': store_visit.status,
                    'route_name': store_visit.route.name if store_visit.route else None
                }
            )
        return None

