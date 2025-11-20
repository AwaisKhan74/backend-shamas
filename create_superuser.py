#!/usr/bin/env python3
"""
Script to create Django superuser non-interactively.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shams_vision.settings')
django.setup()

from users.models import User

def create_superuser():
    """Create a superuser if it doesn't exist."""
    username = os.environ.get('SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('SUPERUSER_EMAIL', 'admin@shamsvision.com')
    password = os.environ.get('SUPERUSER_PASSWORD', 'admin123')
    work_id = os.environ.get('SUPERUSER_WORK_ID', 'ADMIN001')
    
    # Check if superuser already exists
    if User.objects.filter(username=username).exists():
        print(f"❌ User '{username}' already exists!")
        return False
    
    if User.objects.filter(email=email).exists():
        print(f"❌ User with email '{email}' already exists!")
        return False
    
    if User.objects.filter(work_id=work_id).exists():
        print(f"❌ User with work_id '{work_id}' already exists!")
        return False
    
    # Create superuser
    try:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            work_id=work_id,
            role='ADMIN',
            first_name='Admin',
            last_name='User'
        )
        print("=" * 60)
        print("✅ SUPERUSER CREATED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Work ID: {work_id}")
        print(f"Password: {password}")
        print(f"Role: ADMIN")
        print("\n⚠️  IMPORTANT: Change the password after first login!")
        print("\nYou can now login at: http://127.0.0.1:8000/admin/")
        print("=" * 60)
        return True
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_superuser()
    sys.exit(0 if success else 1)


