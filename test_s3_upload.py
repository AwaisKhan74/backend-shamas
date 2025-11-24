#!/usr/bin/env python3
"""
Test script to verify S3 image upload functionality.
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shams_vision.settings')
django.setup()

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import FileManager
from users.models import User

def test_s3_configuration():
    """Check S3 configuration."""
    print("=" * 60)
    print("S3 Configuration Check")
    print("=" * 60)
    print(f"USE_S3_STORAGE: {getattr(settings, 'USE_S3_STORAGE', False)}")
    print(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set')}")
    print(f"AWS_STORAGE_BUCKET_NAME: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Not set')}")
    print(f"AWS_S3_REGION_NAME: {getattr(settings, 'AWS_S3_REGION_NAME', 'Not set')}")
    print(f"MEDIA_URL: {getattr(settings, 'MEDIA_URL', 'Not set')}")
    print()
    
    use_s3 = getattr(settings, 'USE_S3_STORAGE', False)
    if use_s3:
        print("✅ S3 Storage is ENABLED")
        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
        if bucket:
            print(f"✅ Bucket Name: {bucket}")
        else:
            print("⚠️  Bucket name not configured")
    else:
        print("⚠️  S3 Storage is DISABLED (using local storage)")
    print()

def test_file_upload():
    """Test file upload to S3."""
    print("=" * 60)
    print("Testing File Upload")
    print("=" * 60)
    
    # Get or create a test user
    try:
        user = User.objects.filter(role='FIELD_AGENT').first()
        if not user:
            user = User.objects.filter(role='ADMIN').first()
        if not user:
            print("❌ No user found. Please create a user first.")
            return False
        print(f"✅ Using user: {user.email} ({user.role})")
    except Exception as e:
        print(f"❌ Error getting user: {e}")
        return False
    
    # Create a test image file
    test_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    test_file = SimpleUploadedFile(
        name="test_image.png",
        content=test_image_content,
        content_type="image/png"
    )
    
    try:
        # Create FileManager instance
        file_manager = FileManager.objects.create(
            user=user,
            file=test_file,
            file_type='IMAGE',
            purpose='GENERAL',
            description='Test S3 upload verification'
        )
        
        print(f"✅ File uploaded successfully!")
        print(f"   File ID: {file_manager.id}")
        print(f"   File Name: {file_manager.file_name}")
        print(f"   File Size: {file_manager.file_size} bytes")
        print(f"   Content Type: {file_manager.content_type}")
        print(f"   Bucket: {file_manager.bucket}")
        print(f"   Object Key: {file_manager.object_key}")
        print(f"   File URL: {file_manager.file_url}")
        print()
        
        # Check if it's S3 URL
        if file_manager.file_url and 's3' in file_manager.file_url:
            print("✅ SUCCESS: File is stored in S3!")
            print(f"   S3 URL: {file_manager.file_url}")
        elif file_manager.file_url and file_manager.file_url.startswith('/media/'):
            print("⚠️  WARNING: File is stored locally, not in S3")
            print(f"   Local URL: {file_manager.file_url}")
        else:
            print(f"⚠️  File URL: {file_manager.file_url}")
        
        # Check bucket
        if file_manager.bucket:
            print(f"✅ Bucket metadata stored: {file_manager.bucket}")
        else:
            print("⚠️  Bucket metadata not stored")
        
        # Clean up test file
        print()
        print("Cleaning up test file...")
        file_manager.delete()
        print("✅ Test file deleted")
        
        return True
        
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_s3_configuration()
    print()
    success = test_file_upload()
    print()
    print("=" * 60)
    if success:
        print("✅ S3 Upload Test: PASSED")
    else:
        print("❌ S3 Upload Test: FAILED")
    print("=" * 60)

