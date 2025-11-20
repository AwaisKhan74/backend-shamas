# PostgreSQL Setup Guide

## Prerequisites

1. **PostgreSQL installed** on your system
   - macOS: `brew install postgresql@14` or download from [PostgreSQL website](https://www.postgresql.org/download/)
   - Or use Docker: `docker run --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres`

2. **Create Database**
   ```bash
   # Connect to PostgreSQL
   psql -U postgres
   
   # Create database
   CREATE DATABASE shams_vision;
   
   # Create user (optional, you can use default 'postgres' user)
   CREATE USER shams_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE shams_vision TO shams_user;
   
   # Exit psql
   \q
   ```

## Installation Steps

### 1. Install PostgreSQL Adapter

```bash
pip3 install psycopg2-binary
```

Or install all requirements:
```bash
pip3 install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Database Configuration
DB_NAME=shams_vision
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### 3. Test Database Connection

```bash
python3 manage.py check --database default
```

### 4. Run Migrations

```bash
# Create migrations (if not already created)
python3 manage.py makemigrations

# Apply migrations to PostgreSQL
python3 manage.py migrate
```

### 5. Create Superuser

```bash
python3 manage.py createsuperuser
```

### 6. Test the Setup

```bash
# Run development server
python3 manage.py runserver

# Open Django admin
# Visit: http://127.0.0.1:8000/admin/
```

## Verification

To verify the connection is working:

```bash
# Connect to PostgreSQL and check tables
psql -U postgres -d shams_vision

# List all tables
\dt

# Check users table (example)
SELECT * FROM users LIMIT 5;

# Exit
\q
```

## Troubleshooting

### Connection Error: "could not connect to server"

1. **Check PostgreSQL is running:**
   ```bash
   # macOS
   brew services list
   # or
   pg_isready
   ```

2. **Start PostgreSQL:**
   ```bash
   # macOS
   brew services start postgresql@14
   ```

### Authentication Error

1. **Check database credentials in `.env`**
2. **Verify user exists:**
   ```sql
   \du
   ```

3. **Reset password:**
   ```sql
   ALTER USER postgres WITH PASSWORD 'new_password';
   ```

### Database Does Not Exist

```bash
# Create database
createdb -U postgres shams_vision

# Or via psql
psql -U postgres
CREATE DATABASE shams_vision;
```

### Permission Denied

```sql
-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE shams_vision TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
```

## Using Docker (Alternative)

If you prefer using Docker for PostgreSQL:

```bash
# Run PostgreSQL container
docker run --name postgres-shams \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=shams_vision \
  -p 5432:5432 \
  -d postgres:14

# Your .env should have:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=shams_vision
DB_USER=postgres
DB_PASSWORD=postgres
```

## Production Considerations

For production, update `.env`:

```env
DEBUG=False
SECRET_KEY=your-very-secure-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_NAME=shams_vision_prod
DB_USER=shams_user_prod
DB_PASSWORD=very-secure-password
DB_HOST=your-db-host
DB_PORT=5432
```

Also consider:
- Using connection pooling (pgBouncer)
- SSL connections
- Database backups
- Read replicas for scaling

