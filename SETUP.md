# Setup Guide - Shams Vision Backend

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation Steps

### 1. Install System Dependencies (macOS)

For Pillow to work properly, you need to install image libraries:

```bash
brew install jpeg libpng libtiff webp
```

If you don't have Homebrew installed:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

If Pillow installation fails, try:
```bash
pip3 install Pillow --upgrade
```

Or install from a pre-built wheel:
```bash
pip3 install --only-binary :all: Pillow
```

### 3. Create Database Migrations

```bash
python3 manage.py makemigrations
```

This will create migration files for all apps:
- users
- core
- operations
- administration
- finance
- settings
- dashboard

### 4. Apply Migrations

```bash
python3 manage.py migrate
```

This creates all database tables.

### 5. Create Superuser

```bash
python3 manage.py createsuperuser
```

Follow the prompts to create an admin user.

### 6. Run Development Server

```bash
python3 manage.py runserver
```

Visit http://127.0.0.1:8000/admin/ to access Django admin.

## Troubleshooting

### Pillow Installation Issues

If you encounter issues installing Pillow:

1. **macOS**: Install system libraries first:
   ```bash
   brew install jpeg libpng libtiff webp
   ```

2. **Alternative**: Use a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Use pre-built wheel**:
   ```bash
   pip3 install --only-binary :all: Pillow
   ```

### Database Issues

If migrations fail:
1. Delete `db.sqlite3` (if using SQLite)
2. Delete all migration files except `__init__.py` in each app's `migrations/` folder
3. Run `python3 manage.py makemigrations` again
4. Run `python3 manage.py migrate`

## Next Steps

After successful setup:

1. **Create API Serializers**: Build REST API serializers for all models
2. **Create API Views**: Implement ViewSets and endpoints
3. **Implement Authentication**: Build login, OTP, password reset
4. **Add Permissions**: Implement role-based access control
5. **Write Tests**: Create unit and integration tests

See `IMPLEMENTATION_PLAN.md` for detailed next steps.

