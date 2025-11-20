# Django Admin Panel Credentials

## Superuser Account

**Username**: `admin`  
**Email**: `admin@shamsvision.com`  
**Work ID**: `ADMIN001`  
**Password**: `admin123`  
**Role**: `ADMIN`

## Access Admin Panel

1. **Start the development server**:
   ```bash
   python3 manage.py runserver
   ```

2. **Open your browser** and navigate to:
   ```
   http://127.0.0.1:8000/admin/
   ```

3. **Login** with the credentials above

## ⚠️ Security Note

**IMPORTANT**: Change the password immediately after first login!

To change password:
1. Login to admin panel
2. Go to Users → Select your user
3. Change password section
4. Enter new password and save

## Create Additional Superusers

### Option 1: Using the Script (Non-Interactive)

```bash
# Set environment variables
export SUPERUSER_USERNAME=your_username
export SUPERUSER_EMAIL=your_email@example.com
export SUPERUSER_PASSWORD=your_password
export SUPERUSER_WORK_ID=ADMIN002

# Run script
python3 create_superuser.py
```

### Option 2: Using Django Command (Interactive)

```bash
python3 manage.py createsuperuser
```

This will prompt you for:
- Username
- Email address
- Password
- Work ID (if using custom User model)

## Available Models in Admin

Once logged in, you can manage:

### Users App
- Users
- OTPs
- Password Reset Tokens

### Core App
- Counters
- Stores
- Routes
- Route Stores
- **File Manager** (newly added)

### Operations App
- Check Ins
- Breaks
- Store Visits
- Images
- Permission Forms

### Administration App
- Leave Requests
- Penalties
- Daily Summaries

### Finance App
- Rewards
- User Rewards
- Withdrawals
- Finance Transactions

### Settings App
- System Settings
- Profile Settings
- Counter Settings
- Leave Settings
- Report Settings
- Support Tickets
- Quality Checks

### Dashboard App
- Insight Panels
- Datasets
- Downloadable Files
- Download History
- FAQs

## Troubleshooting

### Can't Login
- Verify server is running: `python3 manage.py runserver`
- Check credentials are correct
- Verify user exists: `python3 manage.py shell` → `User.objects.filter(is_superuser=True)`

### Permission Denied
- Verify user has `is_superuser=True`
- Check user role is `ADMIN`
- Verify `is_active=True`

### Reset Password
```bash
python3 manage.py shell
```

```python
from users.models import User
user = User.objects.get(username='admin')
user.set_password('new_password')
user.save()
```

## Next Steps

1. ✅ Login to admin panel
2. ✅ Change default password
3. ✅ Explore all models
4. ✅ Create test data if needed
5. ✅ Configure admin interfaces as needed


