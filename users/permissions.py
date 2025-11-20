"""
Permission classes for role-based access control.
"""
from rest_framework import permissions


class IsFieldAgent(permissions.BasePermission):
    """
    Permission class to check if user is a field agent.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'FIELD_AGENT'
        )


class IsManager(permissions.BasePermission):
    """
    Permission class to check if user is a manager.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'MANAGER'
        )


class IsAdmin(permissions.BasePermission):
    """
    Permission class to check if user is an admin.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ADMIN'
        )


class IsManagerOrAdmin(permissions.BasePermission):
    """
    Permission class to check if user is a manager or admin.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['MANAGER', 'ADMIN']
        )


class IsOwnerOrManagerOrAdmin(permissions.BasePermission):
    """
    Permission class to check if user owns the object or is a manager/admin.
    """

    def has_object_permission(self, request, view, obj):
        # Check if user owns the object
        if hasattr(obj, 'user') and obj.user == request.user:
            return True

        # Check if user is manager or admin
        return request.user.role in ['MANAGER', 'ADMIN']


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission class to allow read access to all, but write access only to owners.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Write permissions only to owners
        if hasattr(obj, 'user'):
            return obj.user == request.user

        return False
"""
Permission classes for role-based access control.
"""
from rest_framework import permissions


class IsFieldAgent(permissions.BasePermission):
    """
    Permission class to check if user is a field agent.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'FIELD_AGENT'
        )


class IsManager(permissions.BasePermission):
    """
    Permission class to check if user is a manager.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'MANAGER'
        )


class IsAdmin(permissions.BasePermission):
    """
    Permission class to check if user is an admin.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ADMIN'
        )


class IsManagerOrAdmin(permissions.BasePermission):
    """
    Permission class to check if user is a manager or admin.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['MANAGER', 'ADMIN']
        )


class IsOwnerOrManagerOrAdmin(permissions.BasePermission):
    """
    Permission class to check if user owns the object or is a manager/admin.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if user owns the object
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Check if user is manager or admin
        return request.user.role in ['MANAGER', 'ADMIN']


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission class to allow read access to all, but write access only to owners.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Write permissions only to owners
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False

