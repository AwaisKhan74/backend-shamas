# Django-Storages Implementation

## Overview

The file storage system has been updated to use **django-storages** properly instead of manual file handling. This follows the official [django-storages documentation](https://django-storages.readthedocs.io/en/latest/).

## Changes Made

### 1. Settings Configuration (`shams_vision/settings.py`)

Updated to follow django-storages best practices:

```python
# django-storages S3 configuration
if USE_S3_STORAGE:
    # AWS Credentials
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
    
    # S3 Settings
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None  # Files are private by default
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',  # Cache for 1 day
    }
    
    # Use S3Boto3Storage for file storage
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

**Key Points:**
- Automatically uses S3 when `USE_S3_STORAGE=True`
- Falls back to local file storage when `USE_S3_STORAGE=False`
- Properly configured MEDIA_URL for S3 or local storage

### 2. FileManager Model (`core/models.py`)

Updated the `save()` method to work with django-storages:

**Before:** Manual S3 operations with boto3
**After:** Let django-storages handle file upload, just extract metadata

#### Key Changes:

1. **File Upload**: django-storages automatically handles:
   - Uploading to S3 (when `USE_S3_STORAGE=True`)
   - File path generation
   - URL generation

2. **Metadata Extraction**: The save method now:
   - Extracts file metadata (name, size, content_type) from the file object
   - Gets object_key from `self.file.name` (set by django-storages)
   - Gets bucket name from storage backend
   - Calculates MD5 checksum if needed

3. **No Manual S3 Operations**: Removed all manual boto3/S3 operations

### 3. How It Works

#### When `USE_S3_STORAGE=False` (Local Storage):
- Files are saved to `MEDIA_ROOT/file_manager/YYYY/MM/DD/`
- `self.file.url` returns local file URL
- `self.file.name` contains relative path

#### When `USE_S3_STORAGE=True` (S3 Storage):
- Files are automatically uploaded to S3 bucket
- `self.file.url` returns S3 URL (with custom domain if configured)
- `self.file.name` contains S3 object key/path
- django-storages handles all S3 operations

## Usage

### Uploading Files

```python
# In your view/serializer
file_manager = FileManager.objects.create(
    user=request.user,
    file=uploaded_file,  # Django FileField handles the rest
    file_type='IMAGE',
    purpose='PROFILE_IMAGE'
)

# django-storages automatically:
# - Uploads to S3 (if configured)
# - Sets file.name to the storage path
# - Makes file.url available
```

### Accessing Files

```python
# Get file URL (works for both S3 and local)
file_url = file_manager.file.url

# Get file metadata
file_name = file_manager.file_name
file_size = file_manager.file_size
content_type = file_manager.content_type
bucket = file_manager.bucket
object_key = file_manager.object_key
```

## Environment Variables

Add to your `.env` file:

```env
# Enable S3 storage
USE_S3_STORAGE=True

# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=us-east-1

# Optional: Custom domain
AWS_S3_CUSTOM_DOMAIN=cdn.example.com

# Optional: Query string auth (False for public files)
AWS_QUERYSTRING_AUTH=True
```

## Benefits

1. **Automatic Handling**: django-storages handles all S3 operations
2. **No Manual Code**: No need to write boto3 code
3. **Seamless Switching**: Toggle between S3 and local storage with one setting
4. **Best Practices**: Follows django-storages recommended configuration
5. **Maintainable**: Less code to maintain, uses well-tested library

## Testing

To test file uploads:

1. **Local Storage** (default):
   ```bash
   # Files saved to: media/file_manager/YYYY/MM/DD/
   ```

2. **S3 Storage**:
   ```bash
   # Set USE_S3_STORAGE=True in .env
   # Files automatically uploaded to S3
   ```

## References

- [django-storages Documentation](https://django-storages.readthedocs.io/en/latest/)
- [S3 Backend Documentation](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html)

