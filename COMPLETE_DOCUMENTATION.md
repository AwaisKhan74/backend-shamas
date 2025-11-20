# Complete Documentation - Shams Vision Backend

## Table of Contents

1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Django Apps Explained](#django-apps-explained)
4. [Models & Database Design](#models--database-design)
5. [Serializers Explained](#serializers-explained)
6. [Permissions & Security](#permissions--security)
7. [Utilities & Helper Functions](#utilities--helper-functions)
8. [Settings Configuration](#settings-configuration)
9. [Best Practices Implemented](#best-practices-implemented)
10. [Why Each Component Exists](#why-each-component-exists)

---

## Project Overview

**Shams Vision** is a comprehensive field agent management system built with Django and Django REST Framework. It supports three user roles (Field Agent, Manager, Admin) and handles route management, store visits, financial operations, and administrative tasks.

**Technology Stack:**
- Django 5.2.7 - Web framework
- Django REST Framework 3.15.2 - API framework
- PostgreSQL 14 - Database

---

## Project Structure

```
shams_vision/
├── shams_vision/          # Main project directory
│   ├── settings.py        # Django settings
│   ├── urls.py            # Root URL configuration
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
├── users/                 # User authentication app
├── core/                  # Core operational models
├── operations/            # Field agent operations
├── administration/        # Administrative features
├── finance/               # Financial management
├── settings/              # System settings & support
├── dashboard/             # Dashboard & analytics
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables
```

**Why This Structure?**
- **Separation of Concerns**: Each app handles a specific domain
- **Modularity**: Easy to maintain and extend
- **Scalability**: Can scale individual components
- **Team Collaboration**: Different developers can work on different apps

---

## Django Apps Explained

### 1. **users** App

**Purpose**: Handles user authentication, authorization, and user management.

**Why We Need It:**
- Custom user model with work_id and roles
- OTP-based authentication for security
- Password reset functionality
- User profile management

**Components:**
- `models.py` - User, OTP, PasswordResetToken models
- `serializers.py` - User data serialization
- `permissions.py` - Role-based permissions
- `utils.py` - Authentication utilities
- `admin.py` - Django admin configuration

**Key Features:**
- Custom User model extending AbstractUser
- Three roles: FIELD_AGENT, MANAGER, ADMIN
- OTP generation and verification
- Secure password reset tokens

---

### 2. **core** App

**Purpose**: Core operational models that form the foundation of the system.

**Why We Need It:**
- Stores represent physical locations
- Routes define daily work assignments
- Counters link to field agents
- RouteStore manages many-to-many relationships

**Components:**
- `models.py` - Counter, Store, Route, RouteStore
- `serializers.py` - Data serialization for core models
- `permissions.py` - Access control for core operations
- `admin.py` - Admin interfaces

**Key Features:**
- GPS coordinate tracking for stores
- Route assignment with priority/order
- Status management (ACTIVE/INACTIVE, PENDING/APPROVED)

---

### 3. **operations** App

**Purpose**: Handles day-to-day field agent operations.

**Why We Need It:**
- Tracks daily check-ins
- Manages store visits
- Records breaks during routes
- Stores images captured during visits
- Handles permission forms

**Components:**
- `models.py` - CheckIn, Break, StoreVisit, Image, PermissionForm
- `serializers.py` - Operation data serialization
- `admin.py` - Admin interfaces

**Key Features:**
- GPS tracking for check-ins and visits
- Time-based tracking (entry/exit times)
- Image uploads with categorization
- AI/ML integration points for quality checks

---

### 4. **administration** App

**Purpose**: Administrative features for managers and admins.

**Why We Need It:**
- Leave request management
- Penalty tracking
- Daily performance summaries
- Manager approval workflows

**Components:**
- `models.py` - LeaveRequest, Penalty, DailySummary
- `serializers.py` - Administrative data serialization
- `admin.py` - Admin interfaces

**Key Features:**
- Leave approval workflow
- Automatic penalty detection
- Performance metrics aggregation
- Status tracking (PENDING/APPROVED/REJECTED)

---

### 5. **finance** App

**Purpose**: Financial management and reward system.

**Why We Need It:**
- Reward type definitions
- User reward tracking
- Withdrawal requests
- Financial transaction history

**Components:**
- `models.py` - Reward, UserReward, Withdrawal, FinanceTransaction
- `serializers.py` - Financial data serialization
- `admin.py` - Admin interfaces

**Key Features:**
- Reward point system
- Withdrawal approval workflow
- Complete transaction history
- Financial reporting capabilities

---

### 6. **settings** App

**Purpose**: System-wide settings and support features.

**Why We Need It:**
- System configuration
- User profile settings
- Support ticket management
- Quality check tracking
- Leave policy settings

**Components:**
- `models.py` - SystemSetting, ProfileSetting, CounterSetting, etc.
- `serializers.py` - Settings data serialization
- `admin.py` - Admin interfaces

**Key Features:**
- Flexible settings storage (JSON)
- Role-based access to settings
- Support ticket workflow
- Quality check integration

---

### 7. **dashboard** App

**Purpose**: Dashboard, analytics, and reporting features.

**Why We Need It:**
- Interactive dashboard panels
- Data filtering and exploration
- File downloads
- FAQ management

**Components:**
- `models.py` - InsightPanel, Dataset, DownloadableFile, FAQ
- `serializers.py` - Dashboard data serialization
- `admin.py` - Admin interfaces

**Key Features:**
- Configurable dashboard panels
- Role-based data access
- Download tracking
- FAQ management

---

## Models & Database Design

### Why PostgreSQL?

**PostgreSQL Benefits:**
- **ACID Compliance**: Data integrity guarantees
- **Advanced Features**: JSON fields, full-text search, arrays
- **Performance**: Better than SQLite for production
- **Scalability**: Handles large datasets efficiently
- **Concurrent Access**: Multiple users can access simultaneously

### Model Design Principles

#### 1. **User Model** (`users/models.py`)

```python
class User(AbstractUser):
    work_id = models.CharField(unique=True)  # Business identifier
    role = models.CharField(choices=ROLE_CHOICES)  # Access control
    phone_number = models.CharField(unique=True)  # Contact info
    profile_picture = models.ImageField()  # User avatar
    has_gps_permission = models.BooleanField()  # Mobile app permissions
    has_camera_permission = models.BooleanField()  # Mobile app permissions
```

**Why These Fields?**
- `work_id`: Business requirement - employees identified by work ID
- `role`: Role-based access control (RBAC)
- `phone_number`: OTP delivery for authentication
- `profile_picture`: User identification
- `has_gps_permission`: Track mobile app permissions
- `has_camera_permission`: Track mobile app permissions

**Why Extend AbstractUser?**
- Inherits Django's authentication system
- Adds custom fields without breaking Django features
- Maintains compatibility with Django admin

---

#### 2. **OTP Model** (`users/models.py`)

```python
class OTP(models.Model):
    user = models.ForeignKey(User)
    code = models.CharField(max_length=6)  # 6-digit code
    purpose = models.CharField(choices=['LOGIN', 'PASSWORD_RESET'])
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField()
    is_used = models.BooleanField()
```

**Why This Design?**
- **Security**: Time-limited OTP codes
- **Purpose Tracking**: Different OTPs for login vs password reset
- **Audit Trail**: Track verification and usage
- **Expiry**: Prevents reuse of old codes

**Why Two Flags (is_verified, is_used)?**
- `is_verified`: OTP was checked and is correct
- `is_used`: OTP was used to complete action
- Allows tracking OTP lifecycle

---

#### 3. **Store Model** (`core/models.py`)

```python
class Store(models.Model):
    name = models.CharField()
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    contact_person = models.CharField()
    phone_number = models.CharField()
    status = models.CharField(choices=['ACTIVE', 'INACTIVE'])
```

**Why GPS Coordinates?**
- **Location Tracking**: Verify field agent visits
- **Route Planning**: Calculate distances
- **Geofencing**: Ensure agents are at correct location

**Why DecimalField for Coordinates?**
- Precision: 9 digits, 6 decimal places = ~10cm accuracy
- Efficiency: Smaller than FloatField
- Validation: MinValue/MaxValue validators

---

#### 4. **Route Model** (`core/models.py`)

```python
class Route(models.Model):
    name = models.CharField()
    user = models.ForeignKey(User)  # Assigned field agent
    date = models.DateField()
    status = models.CharField(choices=['PENDING', 'APPROVED', 'STARTED', 'COMPLETED'])
    approved_by = models.ForeignKey(User)  # Manager who approved
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
```

**Why Status-Based Workflow?**
- **PENDING**: Route created, waiting approval
- **APPROVED**: Manager approved, ready to start
- **STARTED**: Field agent began route
- **COMPLETED**: Route finished

**Why Track Times?**
- Performance metrics
- Compliance tracking
- Billing/payroll calculations

---

#### 5. **RouteStore Model** (`core/models.py`)

```python
class RouteStore(models.Model):
    route = models.ForeignKey(Route)
    store = models.ForeignKey(Store)
    order = models.IntegerField()  # Priority/sequence
    status = models.CharField(choices=['PENDING', 'VISITED', 'SKIPPED'])
```

**Why Many-to-Many Through Model?**
- **Extra Fields**: Store order/priority in route
- **Status Tracking**: Track each store visit individually
- **Flexibility**: Can add more fields later (e.g., visit duration)

**Why Order Field?**
- Route optimization
- Visit sequence
- Priority management

---

#### 6. **StoreVisit Model** (`operations/models.py`)

```python
class StoreVisit(models.Model):
    user = models.ForeignKey(User)
    route = models.ForeignKey(Route)
    store = models.ForeignKey(Store)
    entry_time = models.DateTimeField()
    exit_time = models.DateTimeField()
    entry_latitude = models.DecimalField()
    entry_longitude = models.DecimalField()
    exit_latitude = models.DecimalField()
    exit_longitude = models.DecimalField()
    status = models.CharField(choices=['IN_PROGRESS', 'COMPLETED', 'SKIPPED'])
    ai_ml_check_status = models.CharField()
    ai_ml_feedback = models.TextField()
```

**Why Track Entry/Exit?**
- Visit duration calculation
- Location verification
- Time tracking for compliance

**Why Separate GPS for Entry/Exit?**
- Verify agent was at store
- Detect if agent moved during visit
- Fraud prevention

**Why AI/ML Check Status?**
- Automated image quality checks
- Flag issues for manual review
- Integration point for ML services

---

#### 7. **Image Model** (`operations/models.py`)

```python
class Image(models.Model):
    store_visit = models.ForeignKey(StoreVisit)
    user = models.ForeignKey(User)
    image_url = models.ImageField()
    image_type = models.CharField(choices=['PRODUCT', 'STOREFRONT', 'OTHER'])
    captured_at = models.DateTimeField()
```

**Why Separate Image Model?**
- Multiple images per visit
- Categorization (product, storefront, etc.)
- Metadata tracking (capture time, user)

**Why ImageField?**
- Django handles file storage
- Automatic path generation
- Media file serving

---

#### 8. **LeaveRequest Model** (`administration/models.py`)

```python
class LeaveRequest(models.Model):
    requester = models.ForeignKey(User)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(choices=['PENDING', 'APPROVED', 'REJECTED'])
    approved_by = models.ForeignKey(User)  # Manager
    approved_at = models.DateTimeField()
```

**Why Approval Workflow?**
- Manager oversight
- Audit trail
- Policy enforcement

**Why Track Approver?**
- Accountability
- Reporting
- Permission checks

---

#### 9. **Penalty Model** (`administration/models.py`)

```python
class Penalty(models.Model):
    user = models.ForeignKey(User)
    route = models.ForeignKey(Route, null=True)
    store = models.ForeignKey(Store, null=True)
    reason = models.TextField()
    amount = models.DecimalField()
    penalty_type = models.CharField(choices=['FINANCIAL', 'WARNING'])
    issued_by = models.ForeignKey(User)  # Manager
```

**Why Nullable Route/Store?**
- Penalties can be route-specific, store-specific, or general
- Flexibility for different penalty types

**Why Track Issuer?**
- Authorization (only managers can issue)
- Audit trail
- Accountability

---

#### 10. **DailySummary Model** (`administration/models.py`)

```python
class DailySummary(models.Model):
    counter = models.ForeignKey(User)
    date = models.DateField()
    total_visits = models.IntegerField()
    successful_visits = models.IntegerField()
    skipped_visits = models.IntegerField()
    revenue_generated = models.DecimalField()
    other_metrics = models.JSONField()
```

**Why Pre-Aggregated Data?**
- **Performance**: Faster queries than calculating on-the-fly
- **Reporting**: Quick dashboard updates
- **Analytics**: Historical data for trends

**Why JSONField for Other Metrics?**
- Flexibility: Add new metrics without schema changes
- Future-proof: Can store any metric structure

---

#### 11. **Reward & UserReward Models** (`finance/models.py`)

```python
class Reward(models.Model):
    name = models.CharField()
    points_required = models.IntegerField()
    value = models.DecimalField()  # Monetary value

class UserReward(models.Model):
    user = models.ForeignKey(User)
    reward = models.ForeignKey(Reward)
    amount = models.DecimalField()
    status = models.CharField(choices=['EARNED', 'WITHDRAWN', 'EXPIRED'])
```

**Why Separate Models?**
- **Reward**: Template/definition (reusable)
- **UserReward**: Instance (specific to user)

**Why Status Field?**
- Track reward lifecycle
- Prevent double-withdrawal
- Expiration handling

---

#### 12. **Withdrawal Model** (`finance/models.py`)

```python
class Withdrawal(models.Model):
    user = models.ForeignKey(User)
    reward = models.ForeignKey(UserReward, null=True)
    amount = models.DecimalField()
    status = models.CharField(choices=['PENDING', 'APPROVED', 'REJECTED', 'PROCESSED'])
    processed_by = models.ForeignKey(User)  # Finance admin
    transaction_id = models.CharField()
```

**Why Approval Workflow?**
- Financial control
- Fraud prevention
- Compliance

**Why Transaction ID?**
- Link to payment processor
- Reconciliation
- Audit trail

---

## Serializers Explained

### What Are Serializers?

Serializers convert Django models to JSON (for API responses) and JSON to Django models (for API requests). They also handle validation.

**Why We Need Serializers:**
- **API Compatibility**: Convert models to JSON format
- **Data Validation**: Validate incoming data
- **Data Transformation**: Format data for API responses
- **Security**: Control which fields are exposed

---

### Serializer Types & Their Purpose

#### 1. **UserSerializer** (`users/serializers.py`)

```python
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)
```

**Purpose**: Display user profile information

**Why SerializerMethodField?**
- Computed fields (not in database)
- Custom logic (e.g., `full_name` from `first_name` + `last_name`)

**Why role_display?**
- Human-readable role names
- Frontend can display "Field Agent" instead of "FIELD_AGENT"

**Fields Excluded:**
- `password`: Never expose passwords
- `is_staff`, `is_superuser`: Security-sensitive

---

#### 2. **UserCreateSerializer** (`users/serializers.py`)

```python
class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
```

**Purpose**: User registration

**Why Separate from UserSerializer?**
- Different use case: creation vs display
- Different fields: password during creation, not display
- Different validation: password confirmation

**Why write_only=True?**
- Password never sent in API response
- Security best practice

**Why Password Validators?**
- Enforce password strength
- Use Django's built-in validators
- Consistent security policy

---

#### 3. **UserUpdateSerializer** (`users/serializers.py`)

```python
class UserUpdateSerializer(serializers.ModelSerializer):
    # Only includes updatable fields
```

**Purpose**: Update user profile

**Why Separate Serializer?**
- Different fields: Can't update work_id, email, etc.
- Security: Restrict what users can change
- Validation: Different rules for updates

**Excluded Fields:**
- `work_id`: Immutable identifier
- `email`: Requires verification
- `role`: Only admins can change

---

#### 4. **ChangePasswordSerializer** (`users/serializers.py`)

```python
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
```

**Purpose**: Change user password

**Why Separate Endpoint?**
- Security: Different validation logic
- User experience: Clear purpose
- Security: Verify old password

**Why Verify Old Password?**
- Prevent unauthorized password changes
- Security best practice

---

#### 5. **LoginSerializer** (`users/serializers.py`)

```python
class LoginSerializer(serializers.Serializer):
    work_id = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField()
```

**Purpose**: User login

**Why Serializer Instead of ModelSerializer?**
- No model to serialize
- Custom validation logic
- Flexible input (work_id OR email)

**Why Both work_id and email?**
- User convenience: Login with either
- Business requirement: Employees use work_id

---

#### 6. **OTP Serializers** (`users/serializers.py`)

```python
class GenerateOTPSerializer(serializers.Serializer):
    work_id = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    purpose = serializers.ChoiceField(choices=['LOGIN', 'PASSWORD_RESET'])
```

**Purpose**: Generate OTP for authentication

**Why Multiple Identifiers?**
- Flexibility: User can use work_id, email, or phone
- Recovery: If one fails, try another

**Why Purpose Field?**
- Different OTPs for login vs password reset
- Security: Prevents reuse

---

#### 7. **RouteSerializer** (`core/serializers.py`)

```python
class RouteSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    route_stores = RouteStoreSerializer(many=True, read_only=True)
    stores = serializers.PrimaryKeyRelatedField(many=True, write_only=True)
```

**Purpose**: Route creation and detail view

**Why Nested Serializers?**
- **user_detail**: Show full user info in response
- **route_stores**: Show all stores in route with details

**Why Separate Write Field?**
- **stores**: Accept list of store IDs for creation
- **route_stores**: Show full details in response

**Why write_only for stores?**
- Input: Simple list of IDs
- Output: Full nested details

---

#### 8. **RouteListSerializer** (`core/serializers.py`)

```python
class RouteListSerializer(serializers.ModelSerializer):
    # Minimal fields for performance
```

**Purpose**: Optimized for list views

**Why Separate List Serializer?**
- **Performance**: Less data = faster queries
- **Bandwidth**: Smaller API responses
- **User Experience**: Faster page loads

**Fields Included:**
- Only essential fields
- Computed fields (e.g., stores_count)

**When to Use:**
- List endpoints (GET /api/routes/)
- Detail endpoints use full serializer

---

#### 9. **StoreVisitSerializer** (`operations/serializers.py`)

```python
class StoreVisitSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    store_detail = StoreSerializer(source='store', read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    permission_form = PermissionFormSerializer(read_only=True)
```

**Purpose**: Complete store visit details

**Why Nested Serializers?**
- **user_detail**: Show who visited
- **store_detail**: Show store information
- **images**: Show all captured images
- **permission_form**: Show form data if exists

**Why read_only?**
- Created via separate endpoints
- Prevents nested creation complexity

---

## Permissions & Security

### Permission Classes Explained

#### 1. **IsFieldAgent** (`users/permissions.py`)

```python
class IsFieldAgent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'FIELD_AGENT'
```

**Purpose**: Restrict access to field agents only

**Why We Need It:**
- Route start/end operations
- Store visit submissions
- Check-in operations

**Usage:**
```python
permission_classes = [IsFieldAgent]
```

---

#### 2. **IsManager** (`users/permissions.py`)

```python
class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'MANAGER'
```

**Purpose**: Manager-only operations

**Why We Need It:**
- Route approval
- Leave request approval
- Penalty assignment

---

#### 3. **IsAdmin** (`users/permissions.py`)

```python
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'ADMIN'
```

**Purpose**: Admin-only operations

**Why We Need It:**
- System settings
- User management
- Financial operations

---

#### 4. **IsManagerOrAdmin** (`users/permissions.py`)

```python
class IsManagerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['MANAGER', 'ADMIN']
```

**Purpose**: Shared manager/admin operations

**Why Composite Permission?**
- Reusability: Don't duplicate logic
- Maintainability: Change in one place
- Clarity: Clear intent

---

#### 5. **IsOwnerOrManagerOrAdmin** (`users/permissions.py`)

```python
class IsOwnerOrManagerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        return request.user.role in ['MANAGER', 'ADMIN']
```

**Purpose**: Object-level permission

**Why Object-Level?**
- Users can view their own data
- Managers/admins can view all data
- Different from class-level permission

**Why We Need It:**
- Route viewing: Agents see their routes, managers see all
- Store visits: Agents see their visits, managers see all
- Leave requests: Agents see their requests, managers see all

---

#### 6. **IsOwnerOrReadOnly** (`users/permissions.py`)

```python
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return obj.user == request.user
```

**Purpose**: Read for all, write for owner

**Why We Need It:**
- Public read access (authenticated users)
- Private write access (owner only)

**Usage:**
- Profile viewing: Anyone can view, only owner can edit

---

## Utilities & Helper Functions

### Why Utility Functions?

**Benefits:**
- **Reusability**: Use same logic in multiple places
- **Testability**: Easy to unit test
- **Maintainability**: Change in one place
- **Consistency**: Same behavior everywhere

---

### Utility Functions Explained

#### 1. **generate_otp_code()** (`users/utils.py`)

```python
def generate_otp_code(length=6):
    return ''.join(secrets.choice(string.digits) for _ in range(length))
```

**Purpose**: Generate random 6-digit OTP

**Why secrets module?**
- Cryptographically secure random
- Prevents predictable OTPs
- Security best practice

**Why 6 digits?**
- Balance between security and usability
- Easy to remember and type
- Common industry standard

---

#### 2. **create_otp()** (`users/utils.py`)

```python
def create_otp(user, purpose='LOGIN', expiry_minutes=10):
    # Invalidate previous OTPs
    # Create new OTP
    # Set expiry
```

**Purpose**: Create and manage OTP

**Why Invalidate Previous OTPs?**
- Security: Only one active OTP at a time
- Prevents confusion: Clear which OTP is valid
- Prevents replay attacks

**Why Expiry?**
- Security: Time-limited codes
- Prevents old code reuse
- Industry standard (10 minutes)

---

#### 3. **verify_otp()** (`users/utils.py`)

```python
def verify_otp(user, code, purpose='LOGIN'):
    # Find OTP
    # Check validity
    # Mark as verified
    return (success, otp, message)
```

**Purpose**: Verify OTP code

**Why Return Tuple?**
- Clear success/failure
- Return OTP instance for further use
- Descriptive error messages

**Why Check is_valid()?**
- Centralized validation logic
- Prevents code reuse
- Checks expiry

---

#### 4. **create_password_reset_token()** (`users/utils.py`)

```python
def create_password_reset_token(user, expiry_hours=24):
    # Generate secure token
    # Create token record
    # Set expiry
```

**Purpose**: Create password reset token

**Why Token Instead of OTP?**
- Longer expiry (24 hours vs 10 minutes)
- Email link friendly
- Single-use token

**Why 24 Hours?**
- Balance security and usability
- User has time to check email
- Not too long (security risk)

---

## Settings Configuration

### Why Environment Variables?

**Benefits:**
- **Security**: Secrets not in code
- **Flexibility**: Different configs for dev/prod
- **Version Control**: .env not committed
- **12-Factor App**: Industry best practice

---

### Settings Explained

#### 1. **Database Configuration**

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='shams_vision'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
```

**Why config() Function?**
- Load from .env file
- Fallback to defaults
- Type casting (int, bool, etc.)

**Why Defaults?**
- Development convenience
- Production: Override in .env
- Docker: Use environment variables

---

#### 2. **REST Framework Configuration**

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

**Why SessionAuthentication?**
- Simple for web apps
- Works with Django admin
- Can add JWT later if needed

**Why Default Permission?**
- Secure by default
- Override per view if needed
- Prevents accidental public access

**Why Pagination?**
- Performance: Limit response size
- User experience: Manageable data
- Industry standard

---

#### 3. **CORS Configuration**

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True
```

**Why CORS?**
- Frontend on different domain/port
- Browser security: Blocks cross-origin requests
- Enable API access from frontend

**Why Specific Origins?**
- Security: Only allow trusted origins
- Prevents unauthorized access
- Production: Add production domain

---

#### 4. **Media Files Configuration**

```python
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**Why Separate Media?**
- User uploads (images, files)
- Not in static files (code/assets)
- Separate storage for scalability

**Why BASE_DIR?**
- Relative to project root
- Works across different environments
- Easy to configure

---

## Best Practices Implemented

### 1. **Code Organization**

**What We Did:**
- Separate apps by domain
- Clear file structure
- Consistent naming

**Why:**
- Maintainability
- Team collaboration
- Scalability

---

### 2. **Security**

**What We Did:**
- Password hashing (Django handles)
- OTP-based authentication
- Role-based permissions
- Environment variables for secrets

**Why:**
- Protect user data
- Prevent unauthorized access
- Industry standards

---

### 3. **Performance**

**What We Did:**
- Database indexing
- Optimized list serializers
- Efficient queries (select_related, prefetch_related ready)

**Why:**
- Faster API responses
- Better user experience
- Scalability

---

### 4. **Validation**

**What We Did:**
- Field-level validation
- Cross-field validation
- Model-level validation
- Business logic validation

**Why:**
- Data integrity
- User experience (clear errors)
- Security (prevent invalid data)

---

### 5. **Reusability**

**What We Did:**
- Utility functions
- Reusable permission classes
- Common serializer patterns

**Why:**
- DRY principle (Don't Repeat Yourself)
- Consistency
- Maintainability

---

## Why Each Component Exists

### Summary Table

| Component | Purpose | Why We Need It |
|-----------|---------|----------------|
| **User Model** | User authentication & roles | Core requirement - who can use the system |
| **OTP Model** | Two-factor authentication | Security - verify user identity |
| **Store Model** | Physical locations | Business requirement - where agents visit |
| **Route Model** | Daily work assignments | Business requirement - organize work |
| **StoreVisit Model** | Track visits | Business requirement - record work done |
| **Image Model** | Store photos | Business requirement - proof of visit |
| **LeaveRequest Model** | Time off requests | HR requirement - manage absences |
| **Penalty Model** | Track violations | Business requirement - accountability |
| **Reward Model** | Incentive system | Business requirement - motivation |
| **Withdrawal Model** | Cash out rewards | Business requirement - reward payout |
| **Serializers** | API data format | Required for REST API |
| **Permissions** | Access control | Security - who can do what |
| **Utilities** | Reusable functions | DRY principle - avoid duplication |
| **Settings** | Configuration | Flexibility - different environments |

---

## Conclusion

This documentation explains the **what**, **why**, and **how** of each component in the Shams Vision backend. Each component was designed with:

1. **Purpose**: Clear business requirement
2. **Best Practices**: Industry standards
3. **Security**: Protection of data and access
4. **Scalability**: Can grow with the business
5. **Maintainability**: Easy to update and extend

The codebase follows Django and DRF best practices, ensuring a robust, secure, and maintainable backend system.

---

**For specific implementation details, see:**
- `DATABASE_DESIGN.md` - Database schema details
- `POSTGRESQL_SETUP.md` - Database setup guide
- `CODE_REVIEW.md` - Code quality analysis

