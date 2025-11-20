# FileManager Model Documentation

## Overview

The `FileManager` model is a centralized file/image management system that can be referenced across the entire application. It stores images and files associated with users and routes, providing a unified way to manage all file uploads in the system.

## Purpose

**Why We Need FileManager:**
- **Centralized Management**: All files/images in one place
- **Reusability**: Files can be referenced from multiple places
- **Metadata Tracking**: Store file information, size, type, category
- **Organization**: Organize files by user and route
- **Flexibility**: Support for different file types and categories

## Model Location

**App**: `core/models.py`  
**Model**: `FileManager`

## Fields

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `user` | ForeignKey (User) | User who uploaded the file (required) |
| `file` | ImageField | The actual image/file (required) |
| `file_type` | CharField | Type of file: IMAGE, DOCUMENT, VIDEO, OTHER (default: IMAGE) |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `route` | ForeignKey (Route) | Route associated with file (optional) |
| `image_category` | CharField | Category if file_type is IMAGE (PRODUCT, STOREFRONT, SIGNATURE, etc.) |
| `description` | TextField | Description or notes about the file |
| `file_name` | CharField | Original file name (auto-populated) |
| `file_size` | IntegerField | File size in bytes (auto-populated) |
| `is_active` | BooleanField | Whether file is active/visible (default: True) |

### Auto-Generated Fields

| Field | Type | Description |
|-------|------|-------------|
| `created_at` | DateTimeField | When file was uploaded |
| `updated_at` | DateTimeField | When file was last updated |

## Field Choices

### File Type Choices

```python
FILE_TYPE_CHOICES = [
    ('IMAGE', 'Image'),
    ('DOCUMENT', 'Document'),
    ('VIDEO', 'Video'),
    ('OTHER', 'Other'),
]
```

### Image Category Choices

```python
IMAGE_CATEGORY_CHOICES = [
    ('PRODUCT', 'Product'),
    ('STOREFRONT', 'Storefront'),
    ('SIGNATURE', 'Signature'),
    ('ID_PROOF', 'ID Proof'),
    ('INVOICE', 'Invoice'),
    ('RECEIPT', 'Receipt'),
    ('OTHER', 'Other'),
]
```

## Relationships

### User Relationship
```python
user = ForeignKey(User, related_name='managed_files')
```
- **Purpose**: Track who uploaded the file
- **Access**: `user.managed_files.all()` - Get all files uploaded by user
- **Required**: Yes

### Route Relationship
```python
route = ForeignKey(Route, related_name='files', null=True, blank=True)
```
- **Purpose**: Associate file with a specific route
- **Access**: `route.files.all()` - Get all files for a route
- **Required**: No (files can exist without a route)

## Model Methods

### `save()` Method
Automatically populates:
- `file_name`: Extracts from file.name if not provided
- `file_size`: Calculates file size in bytes if not provided

### `file_url` Property
```python
@property
def file_url(self):
    """Return the URL of the file."""
    return self.file.url if self.file else None
```
**Usage**: Access file URL directly: `file_manager.file_url`

### `file_size_mb` Property
```python
@property
def file_size_mb(self):
    """Return file size in megabytes."""
    return round(self.file_size / (1024 * 1024), 2) if self.file_size else None
```
**Usage**: Get file size in MB: `file_manager.file_size_mb`

## Database Table

**Table Name**: `file_manager`

**Indexes**:
- `user` + `created_at` (for user file queries)
- `route` + `created_at` (for route file queries)
- `file_type` (for filtering by type)
- `image_category` (for filtering images)
- `is_active` (for filtering active files)

## Usage Examples

### Creating a FileManager Instance

```python
from core.models import FileManager

# Create file with user and route
file_manager = FileManager.objects.create(
    user=request.user,
    route=route_instance,
    file=uploaded_image,
    file_type='IMAGE',
    image_category='PRODUCT',
    description='Product photo from store visit'
)

# Create file without route
file_manager = FileManager.objects.create(
    user=request.user,
    file=uploaded_image,
    file_type='IMAGE',
    image_category='SIGNATURE',
    description='Customer signature'
)
```

### Querying Files

```python
# Get all files for a user
user_files = FileManager.objects.filter(user=user)

# Get all files for a route
route_files = FileManager.objects.filter(route=route)

# Get all images for a route
route_images = FileManager.objects.filter(
    route=route,
    file_type='IMAGE'
)

# Get product images for a user
product_images = FileManager.objects.filter(
    user=user,
    file_type='IMAGE',
    image_category='PRODUCT'
)

# Get active files only
active_files = FileManager.objects.filter(is_active=True)
```

### Using Relationships

```python
# From User model
user.managed_files.all()  # All files uploaded by user

# From Route model
route.files.all()  # All files associated with route
```

## Serializers

### FileManagerSerializer

**Location**: `core/serializers.py`

**Purpose**: Full file details for detail views

**Fields Exposed**:
- All model fields
- `user_detail`: Full user information
- `route_detail`: Route information (if route exists)
- `file_url`: File URL
- `file_size_mb`: File size in MB
- Display fields for choices

**Usage**:
```python
from core.serializers import FileManagerSerializer

serializer = FileManagerSerializer(file_manager_instance)
data = serializer.data
```

### FileManagerListSerializer

**Location**: `core/serializers.py`

**Purpose**: Optimized for list views (minimal data)

**Fields Exposed**:
- `id`, `user_detail`, `route_detail`, `file_url`
- `file_type`, `image_category`, `file_name`
- `file_size_mb`, `is_active`, `created_at`

**Usage**:
```python
from core.serializers import FileManagerListSerializer

files = FileManager.objects.all()
serializer = FileManagerListSerializer(files, many=True)
data = serializer.data
```

## Validation

### Automatic Validation

1. **Image Category Required**: If `file_type` is 'IMAGE', `image_category` must be provided
2. **File Size**: Automatically calculated on save
3. **File Name**: Automatically extracted from file

### Serializer Validation

```python
# Validates image_category is provided for images
if file_type == 'IMAGE' and not image_category:
    raise ValidationError('Image category is required')
```

## File Storage

**Upload Path**: `file_manager/%Y/%m/%d/`

**Example**: `file_manager/2024/01/15/image.jpg`

**Why Date-Based Paths?**
- Organization: Files organized by date
- Performance: Faster directory traversal
- Cleanup: Easy to archive old files

## Admin Interface

**Location**: `core/admin.py`

**Features**:
- List view with filters (file_type, image_category, is_active, date)
- Search by file name, user, route, description
- Display file size in MB
- Date hierarchy for easy navigation

**Access**: Django Admin → Core → File Managers

## Use Cases

### 1. Store Visit Images
```python
# Upload image during store visit
file = FileManager.objects.create(
    user=field_agent,
    route=current_route,
    file=image_file,
    file_type='IMAGE',
    image_category='PRODUCT',
    description='Product shelf image'
)
```

### 2. Signature Capture
```python
# Capture signature
file = FileManager.objects.create(
    user=field_agent,
    route=current_route,
    file=signature_image,
    file_type='IMAGE',
    image_category='SIGNATURE',
    description='Customer signature'
)
```

### 3. Document Upload
```python
# Upload invoice or receipt
file = FileManager.objects.create(
    user=field_agent,
    route=current_route,
    file=invoice_pdf,
    file_type='DOCUMENT',
    description='Invoice PDF'
)
```

### 4. Route Documentation
```python
# Upload route-related images
file = FileManager.objects.create(
    user=field_agent,
    route=route,
    file=route_image,
    file_type='IMAGE',
    image_category='STOREFRONT',
    description='Storefront photo'
)
```

## Integration with Other Models

### Referencing from StoreVisit
```python
# In StoreVisit model, you can reference FileManager
class StoreVisit(models.Model):
    # ... other fields ...
    
    # Reference files via route
    def get_images(self):
        return FileManager.objects.filter(
            route=self.route,
            file_type='IMAGE',
            image_category='PRODUCT'
        )
```

### Referencing from Route
```python
# Get all files for a route
route = Route.objects.get(id=1)
route_files = route.files.all()

# Get only images
route_images = route.files.filter(file_type='IMAGE')
```

## Best Practices

1. **Always Set Image Category**: When uploading images, always specify `image_category`
2. **Use Descriptions**: Add meaningful descriptions for better organization
3. **Set is_active=False**: Instead of deleting, set `is_active=False` for soft delete
4. **Organize by Route**: Link files to routes when possible for better organization
5. **Use Appropriate File Types**: Choose correct `file_type` for better filtering

## Migration

**Migration File**: `core/migrations/0003_filemanager.py`

**To Apply**:
```bash
python3 manage.py migrate core
```

**Status**: ✅ Migration created and applied

## Summary

The `FileManager` model provides:
- ✅ Centralized file/image management
- ✅ User and route associations
- ✅ File type and category classification
- ✅ Automatic metadata tracking
- ✅ Flexible querying options
- ✅ Reusable across the application

**This model can be referenced anywhere in the app where you need to store or retrieve images/files associated with users and routes.**

