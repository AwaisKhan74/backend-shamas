# Quick Reference Guide - Shams Vision Backend

## 📚 Documentation Files

- **COMPLETE_DOCUMENTATION.md** - Full detailed documentation (1227 lines)
- **QUICK_REFERENCE.md** - This file (quick lookup)
- **POSTGRESQL_SETUP.md** - Database setup guide
- **QUICK_START_POSTGRES.md** - Quick start instructions

---

## 🏗️ Project Structure

```
shams_vision/
├── users/          → Authentication & user management
├── core/           → Stores, Routes, Counters
├── operations/     → Check-ins, Store visits, Images
├── administration/ → Leaves, Penalties, Summaries
├── finance/        → Rewards, Withdrawals, Transactions
├── settings/       → System settings, Support, Quality
└── dashboard/      → Analytics, Downloads, FAQs
```

---

## 👥 User Roles

| Role | Permissions |
|------|-------------|
| **FIELD_AGENT** | View own routes, submit visits, request leaves |
| **MANAGER** | Approve routes/leaves, assign penalties, view reports |
| **ADMIN** | Full system access, manage users, financial operations |

---

## 📊 Key Models

### Authentication
- `User` - Custom user with work_id and roles
- `OTP` - One-time passwords for login
- `PasswordResetToken` - Password reset tokens

### Core Operations
- `Store` - Physical store locations
- `Route` - Daily work assignments
- `RouteStore` - Links stores to routes (order/priority)
- `Counter` - Field agent profiles

### Field Operations
- `CheckIn` - Daily check-ins with GPS
- `StoreVisit` - Individual store visits
- `Break` - Break tracking
- `Image` - Photos captured during visits
- `PermissionForm` - Optional permission forms

### Administration
- `LeaveRequest` - Leave requests with approval
- `Penalty` - Penalties for violations
- `DailySummary` - Performance summaries

### Finance
- `Reward` - Reward type definitions
- `UserReward` - Rewards awarded to users
- `Withdrawal` - Withdrawal requests
- `FinanceTransaction` - All financial transactions

---

## 🔐 Serializers Overview

### User Serializers (`users/serializers.py`)
- `UserSerializer` - Profile display
- `UserCreateSerializer` - Registration
- `UserUpdateSerializer` - Profile updates
- `ChangePasswordSerializer` - Password changes
- `LoginSerializer` - Login
- `GenerateOTPSerializer` - OTP generation
- `VerifyOTPSerializer` - OTP verification

### Core Serializers (`core/serializers.py`)
- `CounterSerializer` - Counter profiles
- `StoreSerializer` - Store locations
- `RouteSerializer` - Routes (full detail)
- `RouteListSerializer` - Routes (optimized list)

### Operations Serializers (`operations/serializers.py`)
- `CheckInSerializer` - Check-ins
- `StoreVisitSerializer` - Store visits
- `BreakSerializer` - Breaks
- `ImageSerializer` - Images

---

## 🛡️ Permissions

| Permission Class | Purpose |
|------------------|---------|
| `IsFieldAgent` | Field agent only |
| `IsManager` | Manager only |
| `IsAdmin` | Admin only |
| `IsManagerOrAdmin` | Manager or admin |
| `IsOwnerOrManagerOrAdmin` | Owner or manager/admin |
| `IsOwnerOrReadOnly` | Owner can write, all can read |

---

## 🛠️ Utility Functions (`users/utils.py`)

- `generate_otp_code()` - Generate 6-digit OTP
- `create_otp()` - Create and manage OTP
- `verify_otp()` - Verify OTP code
- `create_password_reset_token()` - Create reset token
- `verify_password_reset_token()` - Verify reset token

---

## ⚙️ Settings Configuration

### Database (PostgreSQL)
```python
DB_NAME=shams_vision
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### Environment Variables (.env)
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Allowed hostnames
- `DB_*` - Database credentials

---

## 🚀 Common Commands

### Database
```bash
# Test connection
python3 setup_postgres.py

# Run migrations
python3 manage.py migrate

# Create migrations
python3 manage.py makemigrations
```

### Docker (PostgreSQL)
```bash
# Start container
docker start postgres-shams

# Stop container
docker stop postgres-shams

# View logs
docker logs postgres-shams
```

### Django
```bash
# Create superuser
python3 manage.py createsuperuser

# Run server
python3 manage.py runserver

# Django shell
python3 manage.py shell

# Check system
python3 manage.py check
```

---

## 📝 Common Patterns

### Creating a Serializer
```python
class MyModelSerializer(serializers.ModelSerializer):
    field_display = serializers.CharField(source='get_field_display', read_only=True)
    
    class Meta:
        model = MyModel
        fields = ['id', 'name', 'field_display']
        read_only_fields = ['id']
```

### Creating a Permission
```python
class MyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'ADMIN'
```

### Using Environment Variables
```python
from decouple import config

MY_SETTING = config('MY_SETTING', default='default_value')
```

---

## 🔍 Quick Lookups

### Find Model by App
- Users: `User`, `OTP`, `PasswordResetToken`
- Core: `Counter`, `Store`, `Route`, `RouteStore`
- Operations: `CheckIn`, `StoreVisit`, `Break`, `Image`, `PermissionForm`
- Administration: `LeaveRequest`, `Penalty`, `DailySummary`
- Finance: `Reward`, `UserReward`, `Withdrawal`, `FinanceTransaction`
- Settings: `SystemSetting`, `ProfileSetting`, `SupportTicket`, `QualityCheck`
- Dashboard: `InsightPanel`, `Dataset`, `DownloadableFile`, `FAQ`

### Find Serializer by Model
- User → `UserSerializer`, `UserCreateSerializer`, `UserUpdateSerializer`
- Route → `RouteSerializer`, `RouteListSerializer`
- StoreVisit → `StoreVisitSerializer`, `StoreVisitListSerializer`

### Find Permission by Role
- Field Agent → `IsFieldAgent`
- Manager → `IsManager`
- Admin → `IsAdmin`
- Manager/Admin → `IsManagerOrAdmin`

---

## 🎯 Design Decisions

### Why PostgreSQL?
- Better performance than SQLite
- Production-ready
- Advanced features (JSON fields, full-text search)
- Concurrent access support

### Why Separate Apps?
- Separation of concerns
- Modularity
- Scalability
- Team collaboration

### Why Multiple Serializers?
- Different use cases (create vs update vs list)
- Security (different fields exposed)
- Performance (optimized list views)

### Why Utility Functions?
- Reusability
- Testability
- Maintainability
- Consistency

---

## 📖 For More Details

See **COMPLETE_DOCUMENTATION.md** for:
- Detailed explanations of each component
- Why each design decision was made
- Code examples and patterns
- Best practices and rationale

---

## 🆘 Troubleshooting

### Database Connection Issues
```bash
# Test connection
python3 setup_postgres.py

# Check container
docker ps | grep postgres

# Check logs
docker logs postgres-shams
```

### Migration Issues
```bash
# Check migrations
python3 manage.py showmigrations

# Reset (development only!)
python3 manage.py migrate --fake users zero
python3 manage.py migrate
```

### Permission Issues
- Check user role in database
- Verify permission class in view
- Check object ownership

---

**Last Updated**: See `COMPLETE_DOCUMENTATION.md` for full details

