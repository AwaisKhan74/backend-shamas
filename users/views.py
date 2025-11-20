"""
API viewsets for user authentication and management.
"""
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .permissions import IsAdmin
from .serializers import (
    AdminUserUpdateSerializer,
    LoginSerializer,
    UserCreateSerializer,
    UserProfileUpdateSerializer,
    UserSerializer,
)


class AuthViewSet(viewsets.GenericViewSet):
    """
    Handles authentication-related actions (login, profile fetch/update).
    """

    serializer_class = LoginSerializer
    queryset = User.objects.none()
    lookup_value_regex = r'\d+'

    def get_permissions(self):
        if self.action in ['profile', 'update_profile']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'login':
            return LoginSerializer
        if self.action == 'update_profile':
            return UserProfileUpdateSerializer
        return UserSerializer

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        """
        Authenticate a user and return JWT tokens plus user data.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        user_serializer = UserSerializer(
            user,
            context=self.get_serializer_context()
        )

        return Response({
            'success': True,
            'message': 'Login successful',
            'access_token': str(access_token),
            'refresh_token': str(refresh),
            'token_type': 'Bearer',
            'expires_in': 3600,
            'user_role': user.role,
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='profile')
    def profile(self, request):
        """
        Return the current authenticated user's profile.
        """
        user = request.user
        serializer = UserSerializer(
            user,
            context=self.get_serializer_context()
        )
        return Response({
            'success': True,
            'user_role': user.role,
            'profile': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put', 'patch'], url_path='profile/update')
    def update_profile(self, request):
        """
        Update the authenticated user's profile details.
        """
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True,
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        detail_serializer = UserSerializer(
            request.user,
            context=self.get_serializer_context()
        )
        return Response({
            'success': True,
            'user_role': request.user.role,
            'profile': detail_serializer.data
        }, status=status.HTTP_200_OK)


class AdminUserViewSet(viewsets.ModelViewSet):
    """
    Admin-only viewset for managing users (list, update, soft delete, bulk delete).
    """

    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return User.objects.all().order_by('work_id')

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['update', 'partial_update', 'admin_update']:
            return AdminUserUpdateSerializer
        return UserSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            paginated_response.data.update({'success': True})
            return paginated_response

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'count': len(serializer.data),
            'results': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        response_serializer = UserSerializer(user, context=self.get_serializer_context())
        headers = self.get_success_headers(response_serializer.data)
        return Response({
            'success': True,
            'message': f'User {user.work_id} created successfully.',
            'user': response_serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        detail_serializer = UserSerializer(
            instance,
            context=self.get_serializer_context()
        )
        return Response({
            'success': True,
            'user': detail_serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.id == instance.id:
            return Response({
                'success': False,
                'error': 'You cannot delete your own account.'
            }, status=status.HTTP_400_BAD_REQUEST)

        instance.soft_delete()
        return Response({
            'success': True,
            'message': f'User {instance.work_id} soft-deleted successfully.'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put', 'patch'], url_path='update')
    def admin_update(self, request, pk=None):
        """
        Maintain backward-compatible /users/<id>/update/ endpoint.
        """
        return self.partial_update(request, pk=pk)

    @action(detail=True, methods=['delete'], url_path='delete')
    def admin_delete(self, request, pk=None):
        """
        Maintain backward-compatible /users/<id>/delete/ endpoint.
        """
        return self.destroy(request, pk=pk)

    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """
        Soft delete multiple users by ID.
        """
        user_ids = request.data.get('user_ids')
        if not isinstance(user_ids, list) or not user_ids:
            return Response({
                'success': False,
                'error': 'user_ids must be a non-empty list.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_ids = [int(uid) for uid in user_ids]
        except (TypeError, ValueError):
            return Response({
                'success': False,
                'error': 'user_ids must contain valid integer IDs.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if request.user.id in user_ids:
            return Response({
                'success': False,
                'error': 'You cannot delete your own account.'
            }, status=status.HTTP_400_BAD_REQUEST)

        users_qs = User.all_objects.filter(is_deleted=False, id__in=user_ids)
        found_ids = set(users_qs.values_list('id', flat=True))
        not_found_ids = sorted(set(user_ids) - found_ids)

        if not users_qs.exists():
            return Response({
                'success': False,
                'error': 'No matching active users found for the provided IDs.',
                'not_found_ids': not_found_ids
            }, status=status.HTTP_404_NOT_FOUND)

        deleted_users = []
        for user in users_qs:
            user.soft_delete()
            deleted_users.append({
                'id': user.id,
                'work_id': user.work_id,
                'username': user.username
            })

        return Response({
            'success': True,
            'deleted_count': len(deleted_users),
            'deleted_users': deleted_users,
            'not_found_ids': not_found_ids
        }, status=status.HTTP_200_OK)
