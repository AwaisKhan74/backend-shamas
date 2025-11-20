# Shams Vision Backend

A comprehensive Django REST Framework backend for field agent management, route tracking, and administrative operations.

## Project Structure

```
shams_vision/
├── shams_vision/          # Main project settings
├── users/                 # User authentication & management
├── core/                  # Core models (Store, Route, Counter)
├── operations/            # Field agent operations (CheckIn, StoreVisit, etc.)
├── administration/        # Administrative features (Leave, Penalty, etc.)
├── finance/               # Financial management (Rewards, Withdrawals)
├── settings/              # System settings & support
└── dashboard/             # Dashboard & analytics

```

## User Roles

1. **FIELD_AGENT** - Field agents who perform daily routes and visit stores
2. **MANAGER** - Managers who approve routes, leave requests, and manage penalties
3. **ADMIN** - System administrators who manage finance, settings, and configurations

## Database Models

### Authentication & Users
- `User` - Custom user model with work_id and roles
- `OTP` - One-time password for login and password reset
- `PasswordResetToken` - Password reset tokens

### Core Operations
- `Counter` - Field agent profiles
- `Store` - Store locations
- `Route` - Daily routes assigned to field agents
- `RouteStore` - Many-to-many relationship between routes and stores

### Field Agent Operations
- `CheckIn` - Daily check-ins with GPS coordinates
- `Break` - Break tracking during routes
- `StoreVisit` - Individual store visits
- `Image` - Images captured during store visits
- `PermissionForm` - Optional permission forms

### Administration
- `LeaveRequest` - Leave requests from field agents
- `Penalty` - Penalties for skipped stores or incomplete routes
- `DailySummary` - Daily performance summaries

### Finance
- `Reward` - Reward types and configurations
- `UserReward` - Rewards awarded to users
- `Withdrawal` - Withdrawal requests
- `FinanceTransaction` - All financial transactions

### Settings & Support
- `SystemSetting` - System-wide configurations
- `ProfileSetting` - User-specific profile settings
- `CounterSetting` - Counter-specific settings
- `LeaveSetting` - Leave policy settings
- `ReportSetting` - Report configurations
- `SupportTicket` - User support tickets
- `QualityCheck` - Quality checks for images and data

### Dashboard
- `InsightPanel` - Interactive dashboard panels
- `Dataset` - Datasets for filtering
- `DownloadableFile` - Files available for download
- `DownloadHistory` - Download tracking
- `FAQ` - Frequently asked questions

## Setup Instructions

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

Note: Pillow may require system libraries (jpeg, zlib, etc.). On macOS, install via Homebrew:
```bash
brew install jpeg libpng libtiff webp
```

### 2. Create Database Migrations

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 3. Create Superuser

```bash
python3 manage.py createsuperuser
```

### 4. Run Development Server

```bash
python3 manage.py runserver
```

## API Endpoints (To Be Implemented)

### Authentication
- `POST /api/auth/login/` - Login with email/work_id and password
- `POST /api/auth/otp/generate/` - Generate OTP
- `POST /api/auth/otp/verify/` - Verify OTP
- `POST /api/auth/password/reset/` - Request password reset
- `POST /api/auth/password/reset/confirm/` - Confirm password reset

### Users
- `GET /api/users/me/` - Get current user profile
- `PUT /api/users/me/` - Update current user profile

### Routes
- `GET /api/routes/` - List routes
- `POST /api/routes/` - Create route
- `GET /api/routes/{id}/` - Get route details
- `POST /api/routes/{id}/start/` - Start route
- `POST /api/routes/{id}/end/` - End route

### Store Visits
- `POST /api/store-visits/` - Create store visit
- `GET /api/store-visits/{id}/` - Get store visit details
- `POST /api/store-visits/{id}/enter/` - Enter store
- `POST /api/store-visits/{id}/exit/` - Exit store
- `POST /api/store-visits/{id}/submit/` - Submit store visit

And many more...

## Next Steps

1. **Create Migrations**: Run `python3 manage.py makemigrations` and `python3 manage.py migrate`
2. **Create API Serializers**: Create serializers for all models
3. **Create API Views**: Implement ViewSets and API endpoints
4. **Implement Authentication**: Build login, OTP verification, password reset
5. **Add Permissions**: Implement role-based access control
6. **Write Tests**: Create unit and integration tests

## Documentation

- See `DATABASE_DESIGN.md` for detailed database schema
- See `IMPLEMENTATION_PLAN.md` for step-by-step implementation guide

## Development

- Python 3.8+
- Django 5.2.7
- Django REST Framework 3.15.2

