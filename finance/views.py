"""
Views for finance app (rewards, points management).
"""
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Sum
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.permissions import IsManagerOrAdmin
from administration.models import Penalty
from .models import Reward, UserReward, UserPoints, PointsTransaction
from .serializers import (
    RewardSerializer,
    UserPointsSerializer,
    PointsTransactionSerializer,
    RewardActivitySerializer,
    UserRewardSerializer,
)
from .services import PointsCalculationService


class RewardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing rewards.
    """
    queryset = Reward.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RewardSerializer
    
    def get_permissions(self):
        """Only admins can create/update/delete rewards."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManagerOrAdmin()]
        return [permissions.IsAuthenticated()]
    
    @action(methods=['get'], detail=False, url_path='my-points')
    def my_points(self, request):
        """
        Get current user's points balance and statistics.
        GET /api/finance/rewards/my-points/
        """
        user = request.user
        
        if user.role != 'FIELD_AGENT':
            return Response({
                'error': 'Only field agents can view their points'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get or create user points
        user_points, created = UserPoints.objects.get_or_create(user=user)
        
        # Calculate month statistics
        today = timezone.now().date()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        # Get current month points
        current_month_points = PointsTransaction.objects.filter(
            user=user,
            transaction_type='EARNED',
            created_at__date__gte=first_day_of_month,
            created_at__date__lte=last_day_of_month
        ).aggregate(total=Sum('points'))['total'] or 0
        
        # Month target (configurable, default 2000)
        month_target = 2000  # TODO: Make this configurable
        month_progress_percentage = (current_month_points / month_target * 100) if month_target > 0 else 0
        
        serializer = UserPointsSerializer(user_points)
        data = serializer.data
        data.update({
            'current_month_points': current_month_points,
            'month_target': month_target,
            'month_progress_percentage': round(month_progress_percentage, 1)
        })
        
        return Response({
            'success': True,
            'points': data
        })
    
    @action(methods=['get'], detail=False, url_path='activity')
    def activity(self, request):
        """
        Get rewards activity for current user.
        GET /api/finance/rewards/activity/?period=this_month
        """
        user = request.user
        
        if user.role != 'FIELD_AGENT':
            return Response({
                'error': 'Only field agents can view their activity'
            }, status=status.HTTP_403_FORBIDDEN)
        
        period = request.query_params.get('period', 'this_month')
        today = timezone.now().date()
        
        # Filter by period
        if period == 'this_month':
            first_day = today.replace(day=1)
            last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            queryset = PointsTransaction.objects.filter(
                user=user,
                transaction_type='EARNED',
                created_at__date__gte=first_day,
                created_at__date__lte=last_day
            )
        elif period == 'previous_month':
            first_day_of_current = today.replace(day=1)
            last_day_of_previous = first_day_of_current - timedelta(days=1)
            first_day_of_previous = last_day_of_previous.replace(day=1)
            queryset = PointsTransaction.objects.filter(
                user=user,
                transaction_type='EARNED',
                created_at__date__gte=first_day_of_previous,
                created_at__date__lte=last_day_of_previous
            )
        else:  # all_time
            queryset = PointsTransaction.objects.filter(
                user=user,
                transaction_type='EARNED'
            )
        
        queryset = queryset.select_related('store', 'store__district').order_by('-created_at')
        serializer = RewardActivitySerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'period': period,
            'activities': serializer.data,
            'count': queryset.count()
        })
    
    @action(methods=['get'], detail=False, url_path='history')
    def history(self, request):
        """
        Get rewards history for current user.
        GET /api/finance/rewards/history/?period=this_month
        """
        # Same as activity but with different endpoint name
        return self.activity(request)


class PenaltyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing penalties.
    """
    queryset = Penalty.objects.select_related('user', 'store', 'store__district', 'route', 'issued_by')
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter penalties based on user role."""
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.role == 'FIELD_AGENT':
            return queryset.filter(user=user)
        elif user.role in ('MANAGER', 'ADMIN'):
            # Can filter by user_id query param
            user_id = self.request.query_params.get('user_id')
            if user_id:
                return queryset.filter(user_id=user_id)
            return queryset
        
        return queryset.none()
    
    def get_serializer_class(self):
        """Use different serializers for list vs detail."""
        if self.action == 'list':
            from administration.serializers import PenaltyListSerializer
            return PenaltyListSerializer
        from administration.serializers import PenaltySerializer
        return PenaltySerializer
    
    def get_permissions(self):
        """Only managers/admins can create penalties."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManagerOrAdmin()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Set issued_by when creating penalty."""
        serializer.save(issued_by=self.request.user)
    
    @action(methods=['get'], detail=False, url_path='summary')
    def summary(self, request):
        """
        Get penalties summary with totals and period filtering.
        GET /api/administration/penalties/summary/?period=this_month
        """
        user = request.user
        period = request.query_params.get('period', 'this_month')
        today = timezone.now().date()
        
        # Get base queryset
        if user.role == 'FIELD_AGENT':
            queryset = Penalty.objects.filter(user=user)
        elif user.role in ('MANAGER', 'ADMIN'):
            user_id = request.query_params.get('user_id')
            if user_id:
                queryset = Penalty.objects.filter(user_id=user_id)
            else:
                queryset = Penalty.objects.all()
        else:
            queryset = Penalty.objects.none()
        
        # Filter by period
        if period == 'this_month':
            first_day = today.replace(day=1)
            last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            queryset = queryset.filter(
                issued_at__date__gte=first_day,
                issued_at__date__lte=last_day
            )
        elif period == 'previous_month':
            first_day_of_current = today.replace(day=1)
            last_day_of_previous = first_day_of_current - timedelta(days=1)
            first_day_of_previous = last_day_of_previous.replace(day=1)
            queryset = queryset.filter(
                issued_at__date__gte=first_day_of_previous,
                issued_at__date__lte=last_day_of_previous
            )
        # all_time - no additional filter
        
        # Calculate totals
        total_penalty = queryset.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        stores_missed = queryset.filter(
            store__isnull=False
        ).values('store').distinct().count()
        
        # Get penalty list
        from administration.serializers import PenaltyListSerializer
        serializer = PenaltyListSerializer(queryset.order_by('-issued_at'), many=True)
        
        return Response({
            'success': True,
            'period': period,
            'total_penalty': float(total_penalty),
            'stores_missed': stores_missed,
            'penalties': serializer.data,
            'count': queryset.count()
        })
    
    def list(self, request, *args, **kwargs):
        """List penalties with summary information."""
        # Use summary endpoint for list view
        period = request.query_params.get('period', 'this_month')
        return self.summary(request)
