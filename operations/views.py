from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from .models import Break, CheckIn, FlaggedStore, PermissionForm, StoreVisit
from .serializers import (
    BreakSerializer,
    CheckInSerializer,
    CheckOutSerializer,
    FlaggedStoreCreateSerializer,
    FlaggedStoreSerializer,
    PermissionFormCreateSerializer,
    PermissionFormSerializer,
    StartBreakSerializer,
    StartDaySerializer,
    StoreVisitCreateSerializer,
    StoreVisitSerializer,
)


class WorkSessionViewSet(viewsets.GenericViewSet):
    """
    Manage the lifecycle of a field agent's workday: start, break, resume, checkout.
    """

    serializer_class = CheckInSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CheckIn.objects.select_related('user').prefetch_related('break_entries__route')

    def get_queryset(self):
        user = self.request.user
        base_qs = super().get_queryset()
        if user.role in ('ADMIN', 'MANAGER'):
            # Allow filtering by user id for supervisors
            target_user_id = self.request.query_params.get('user_id')
            if target_user_id:
                return base_qs.filter(user_id=target_user_id)
            return base_qs
        return base_qs.filter(user=user)

    def _require_field_agent(self, user):
        if user.role != 'FIELD_AGENT':
            raise PermissionDenied("Only field agents can perform this action.")

    def _get_today_session(self, user=None, user_id=None):
        today = timezone.localdate()
        qs = CheckIn.objects.filter(shift_date=today)
        if user_id:
            qs = qs.filter(user_id=user_id)
        elif user is not None:
            qs = qs.filter(user=user)
        else:
            return None
        return qs.first()

    def _get_active_session(self, user):
        session = self._get_today_session(user)
        if session and session.is_active:
            return session
        return None

    @action(methods=['post'], detail=False, url_path='start-day')
    def start_day(self, request):
        """
        Start the field agent's workday (check-in).
        """
        user = request.user
        self._require_field_agent(user)

        if self._get_today_session(user=user):
            raise ValidationError("You have already started today's session.")

        serializer = StartDaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            session = CheckIn.objects.create(
                user=user,
                shift_date=timezone.localdate(),
                timestamp=timezone.now(),
                latitude=serializer.validated_data['latitude'],
                longitude=serializer.validated_data['longitude'],
            )
        except Exception as exc:  # pragma: no cover - integrity safety net
            raise ValidationError(f"Unable to start session: {exc}")
        data = CheckInSerializer(session, context=self.get_serializer_context()).data
        return Response({'success': True, 'session': data}, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False, url_path='take-break')
    def take_break(self, request):
        """
        Start a break during the active session.
        Tracks break time for 9-hour shift calculation.
        Route is optional - breaks are tracked per work session, not per route.
        """
        user = request.user
        self._require_field_agent(user)

        session = self._get_active_session(user)
        if not session:
            raise ValidationError("No active session found for today. Please start your day first.")

        if session.status == CheckIn.Status.ON_BREAK:
            raise ValidationError("You are already on a break. Please resume your work first.")

        serializer = StartBreakSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        route = serializer.validated_data.get('route')  # Optional

        start_time = timezone.now()
        try:
            session.start_break(start_time=start_time)
        except ValueError as exc:
            raise ValidationError(str(exc))

        # Create break entry (route is optional)
        break_entry = Break.objects.create(
            user=user,
            session=session,
            route=route,  # Can be None
            start_time=start_time,
        )

        response_data = {
            'success': True,
            'message': 'Break started successfully',
            'session': CheckInSerializer(session, context=self.get_serializer_context()).data,
            'break': BreakSerializer(break_entry, context=self.get_serializer_context()).data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='resume-day')
    def resume_day(self, request):
        """
        Resume work after a break.
        Updates break duration and continues tracking work hours for 9-hour shift.
        """
        user = request.user
        self._require_field_agent(user)

        session = self._get_today_session(user=user)
        if not session or session.status != CheckIn.Status.ON_BREAK:
            raise ValidationError("There is no break in progress to resume.")

        active_break = session.break_entries.filter(end_time__isnull=True).order_by('-start_time').first()
        if not active_break:
            raise ValidationError("No active break record found.")

        end_time = timezone.now()
        active_break.end_time = end_time
        active_break.calculate_duration()  # Calculate duration
        active_break.save()

        try:
            break_duration = session.resume_from_break(end_time=end_time)
        except ValueError as exc:
            raise ValidationError(str(exc))

        response_data = {
            'success': True,
            'message': f'Resumed from break. Break duration: {break_duration}',
            'session': CheckInSerializer(session, context=self.get_serializer_context()).data,
            'break': BreakSerializer(active_break, context=self.get_serializer_context()).data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='check-out')
    def check_out(self, request):
        """
        Complete the workday (check-out).
        """
        user = request.user
        self._require_field_agent(user)

        session = self._get_today_session(user=user)
        if not session:
            raise ValidationError("No session found for today.")

        if session.status == CheckIn.Status.ON_BREAK:
            raise ValidationError("Resume your session before checking out.")

        if session.status == CheckIn.Status.COMPLETED:
            raise ValidationError("You have already checked out for today.")

        serializer = CheckOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        checkout_time = timezone.now()
        try:
            session.mark_check_out(
                checkout_time=checkout_time,
                latitude=serializer.validated_data.get('latitude'),
                longitude=serializer.validated_data.get('longitude'),
            )
        except ValueError as exc:
            raise ValidationError(str(exc))

        data = CheckInSerializer(session, context=self.get_serializer_context()).data
        return Response({'success': True, 'session': data}, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='current')
    def current(self, request):
        """
        Return current session snapshot for the authenticated user.
        """
        user = request.user
        if user.role == 'FIELD_AGENT':
            session = self._get_today_session(user=user)
        elif user.role in ('MANAGER', 'ADMIN'):
            user_id = request.query_params.get('user_id')
            if not user_id:
                raise ValidationError("Provide a user_id to inspect a session.")
            session = self._get_today_session(user_id=user_id)
        else:
            session = None

        if not session:
            return Response({'success': True, 'session': None})

        data = CheckInSerializer(session, context=self.get_serializer_context()).data
        breaks = session.break_entries.order_by('-start_time')
        break_data = BreakSerializer(breaks, many=True, context=self.get_serializer_context()).data
        return Response({'success': True, 'session': data, 'breaks': break_data})


class StoreVisitViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing store visits.
    """
    queryset = StoreVisit.objects.select_related('user', 'route', 'store', 'approved_by')
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.role == 'FIELD_AGENT':
            return queryset.filter(user=user)
        elif user.role in ('MANAGER', 'ADMIN'):
            # Can filter by user_id query param
            user_id = self.request.query_params.get('user_id')
            if user_id:
                queryset = queryset.filter(user_id=user_id)
            return queryset
        
        return queryset.none()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return StoreVisitCreateSerializer
        return StoreVisitSerializer
    
    @action(methods=['post'], detail=True, url_path='complete')
    def complete(self, request, pk=None):
        """Mark a store visit as completed."""
        visit = self.get_object()
        if visit.status == 'COMPLETED':
            raise ValidationError("Visit is already completed.")
        
        visit.status = 'COMPLETED'
        visit.submitted_at = timezone.now()
        visit.save()
        
        serializer = self.get_serializer(visit)
        return Response({'success': True, 'visit': serializer.data})
    
    @action(methods=['post'], detail=True, url_path='skip')
    def skip(self, request, pk=None):
        """Skip a store visit."""
        visit = self.get_object()
        if visit.status == 'SKIPPED':
            raise ValidationError("Visit is already skipped.")
        
        visit.status = 'SKIPPED'
        visit.save()
        
        serializer = self.get_serializer(visit)
        return Response({'success': True, 'visit': serializer.data})
    
    @action(methods=['post'], detail=True, url_path='submit-permission-form')
    def submit_permission_form(self, request, pk=None):
        """
        Submit a permission form for a store visit.
        POST /api/operations/store-visits/{id}/submit-permission-form/
        """
        visit = self.get_object()
        
        # Check if permission form already exists
        if hasattr(visit, 'permission_form'):
            raise ValidationError("Permission form already submitted for this visit.")
        
        # Only field agents can submit permission forms for their own visits
        if request.user.role == 'FIELD_AGENT' and visit.user != request.user:
            raise PermissionDenied("You can only submit permission forms for your own visits.")
        
        serializer = PermissionFormCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        permission_form = serializer.save()
        
        response_serializer = PermissionFormSerializer(permission_form)
        return Response({
            'success': True,
            'permission_form': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(methods=['get'], detail=True, url_path='permission-form')
    def get_permission_form(self, request, pk=None):
        """
        Get permission form for a store visit.
        GET /api/operations/store-visits/{id}/permission-form/
        """
        visit = self.get_object()
        
        # Check permissions
        if request.user.role == 'FIELD_AGENT' and visit.user != request.user:
            raise PermissionDenied("You can only view permission forms for your own visits.")
        
        if not hasattr(visit, 'permission_form'):
            return Response({
                'success': True,
                'permission_form': None
            })
        
        serializer = PermissionFormSerializer(visit.permission_form)
        return Response({
            'success': True,
            'permission_form': serializer.data
        })
    
    @action(methods=['post'], detail=True, url_path='flag-store')
    def flag_store(self, request, pk=None):
        """
        Flag a store visit with a reason.
        POST /api/operations/store-visits/{id}/flag-store/
        """
        visit = self.get_object()
        
        # Only field agents can flag stores for their own visits
        if request.user.role == 'FIELD_AGENT' and visit.user != request.user:
            raise PermissionDenied("You can only flag stores for your own visits.")
        
        serializer = FlaggedStoreCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        flagged_store = serializer.save()
        
        response_serializer = FlaggedStoreSerializer(flagged_store)
        return Response({
            'success': True,
            'flagged_store': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(methods=['get'], detail=True, url_path='flagged-details')
    def get_flagged_details(self, request, pk=None):
        """
        Get flagged store details for a store visit.
        GET /api/operations/store-visits/{id}/flagged-details/
        """
        visit = self.get_object()
        
        # Check permissions
        if request.user.role == 'FIELD_AGENT' and visit.user != request.user:
            raise PermissionDenied("You can only view flagged details for your own visits.")
        
        if not hasattr(visit, 'flagged_store'):
            return Response({
                'success': True,
                'flagged_store': None
            })
        
        serializer = FlaggedStoreSerializer(visit.flagged_store)
        return Response({
            'success': True,
            'flagged_store': serializer.data
        })
