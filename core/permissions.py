"""
Permission classes for core models.
"""
from rest_framework import permissions
from users.permissions import IsManagerOrAdmin


class CanManageStore(permissions.BasePermission):
    """
    Permission to manage stores (Manager or Admin only).
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return IsManagerOrAdmin().has_permission(request, view)


class CanManageRoute(permissions.BasePermission):
    """
    Permission to manage routes.
    - Field agents can view their own routes
    - Managers/Admins can view and manage all routes
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write operations require Manager or Admin
        return request.user.role in ['MANAGER', 'ADMIN']
    
    def has_object_permission(self, request, view, obj):
        # Field agents can only view/modify their own routes
        if request.user.role == 'FIELD_AGENT':
            return obj.user == request.user
        
        # Managers and Admins can access all routes
        return request.user.role in ['MANAGER', 'ADMIN']


class CanManageCounter(permissions.BasePermission):
    """
    Permission to manage counters (Manager or Admin only).
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return IsManagerOrAdmin().has_permission(request, view)

