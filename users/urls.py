"""
URL configuration for users app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import AdminUserViewSet, AuthViewSet

app_name = 'users'

router = DefaultRouter()
router.register('', AuthViewSet, basename='auth')
router.register('users', AdminUserViewSet, basename='auth-users')

urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token-blacklist'),
    path('', include(router.urls)),
]
