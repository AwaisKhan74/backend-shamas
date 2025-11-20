"""
Utility functions for password reset management.
"""
import secrets
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import PasswordResetToken

User = get_user_model()


def generate_password_reset_token():
    """
    Generate a secure password reset token.
    
    Returns:
        str: Secure random token
    """
    return secrets.token_urlsafe(32)


def create_password_reset_token(user, expiry_hours=24):
    """
    Create a password reset token for the user.
    
    Args:
        user: User instance
        expiry_hours: Token expiry time in hours (default: 24)
    
    Returns:
        PasswordResetToken: Created token instance
    """
    # Invalidate previous unused tokens
    PasswordResetToken.objects.filter(
        user=user,
        is_used=False
    ).update(is_used=True)
    
    # Create new token
    token = generate_password_reset_token()
    expires_at = timezone.now() + timedelta(hours=expiry_hours)
    
    reset_token = PasswordResetToken.objects.create(
        user=user,
        token=token,
        expires_at=expires_at
    )
    
    return reset_token


def verify_password_reset_token(token):
    """
    Verify password reset token.
    
    Args:
        token: Token string to verify
    
    Returns:
        tuple: (success: bool, reset_token: PasswordResetToken or None, message: str)
    """
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        
        if not reset_token.is_valid():
            return False, None, "Token has expired or already been used"
        
        return True, reset_token, "Token verified successfully"
    
    except PasswordResetToken.DoesNotExist:
        return False, None, "Invalid token"

