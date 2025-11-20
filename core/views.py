from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.permissions import IsManagerOrAdmin
from .models import District, FileManager, Store
from .serializers import (
    DistrictListSerializer,
    DistrictSerializer,
    DistrictStatsSerializer,
    FileManagerSerializer,
    FileManagerUploadSerializer,
    StoreSerializer,
)


class FileManagerViewSet(viewsets.ModelViewSet):
    """Expose CRUD for file uploads stored via the configured storage backend."""

    queryset = FileManager.objects.filter(is_active=True).select_related('user', 'route')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FileManagerUploadSerializer
        return FileManagerSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DistrictViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing districts.
    """
    queryset = District.objects.all().prefetch_related('stores')
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DistrictListSerializer
        if self.action == 'today_stats':
            return DistrictStatsSerializer
        return DistrictSerializer
    
    def get_permissions(self):
        """
        Only admins/managers can create/update/delete districts.
        All authenticated users can view.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsManagerOrAdmin()]
        return [permissions.IsAuthenticated()]
    
    @action(methods=['get'], detail=True, url_path='stores')
    def stores(self, request, pk=None):
        """
        Get all stores in a district.
        GET /api/operations/districts/{id}/stores/
        """
        district = self.get_object()
        stores = district.stores.filter(status='ACTIVE')
        
        # Filter by query params if provided
        search = request.query_params.get('search')
        if search:
            stores = stores.filter(
                Q(name__icontains=search) | Q(address__icontains=search)
            )
        
        serializer = StoreSerializer(stores, many=True, context=self.get_serializer_context())
        return Response({
            'success': True,
            'district': DistrictListSerializer(district, context=self.get_serializer_context()).data,
            'stores': serializer.data,
            'count': stores.count()
        })
    
    @action(methods=['get'], detail=False, url_path='today-stats')
    def today_stats(self, request):
        """
        Get today's districts with statistics for the authenticated user.
        GET /api/operations/districts/today-stats/
        
        For field agents: Returns districts from their today's routes.
        For managers/admins: Returns all districts with today's stats.
        """
        from core.models import Route
        
        user = request.user
        today = timezone.localdate()
        
        if user.role == 'FIELD_AGENT':
            # Get districts from user's today's routes
            routes_today = Route.objects.filter(
                user=user,
                date=today,
                status__in=['APPROVED', 'STARTED', 'COMPLETED']
            )
            district_ids = routes_today.filter(district__isnull=False).values_list('district_id', flat=True).distinct()
            districts = District.objects.filter(
                id__in=district_ids,
                status='ACTIVE'
            )
        else:
            # Managers/admins see all districts with today's activity
            districts = District.objects.filter(status='ACTIVE')
        
        serializer = DistrictStatsSerializer(districts, many=True, context=self.get_serializer_context())
        return Response({
            'success': True,
            'date': today.isoformat(),
            'districts': serializer.data,
            'count': districts.count()
        })
