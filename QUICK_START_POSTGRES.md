# Quick Start - PostgreSQL Setup

## Option 1: Install PostgreSQL Locally (macOS)

### Step 1: Install PostgreSQL

```bash
# Using Homebrew
brew install postgresql@14

# Start PostgreSQL service
brew services start postgresql@14

# Or start manually
pg_ctl -D /usr/local/var/postgresql@14 start
```

### Step 2: Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database
CREATE DATABASE shams_vision;

# Exit
\q
```

### Step 3: Create .env File

Create a `.env` file in the project root:

```bash
cat > .env << EOF
SECRET_KEY=django-insecure-&sezm6+4#qhwp^k-*75ap%e!_c@@0*8*6w8w#5rx)fvk7\$vh!n
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=shams_vision
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
EOF
```

### Step 4: Test Connection

```bash
python3 setup_postgres.py
```

### Step 5: Run Migrations

```bash
python3 manage.py migrate
```

## Option 2: Use Docker (Recommended for Development)

### Step 1: Run PostgreSQL Container

```bash
docker run --name postgres-shams \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=shams_vision \
  -p 5432:5432 \
  -d postgres:14
```

### Step 2: Create .env File

```bash
cat > .env << EOF
SECRET_KEY=django-insecure-&sezm6+4#qhwp^k-*75ap%e!_c@@0*8*6w8w#5rx)fvk7\$vh!n
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=shams_vision
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
EOF
```

### Step 3: Test Connection

```bash
python3 setup_postgres.py
```

### Step 4: Run Migrations

```bash
python3 manage.py migrate
```

## Verify Setup

```bash
# Test connection
python3 setup_postgres.py

# Check database
python3 manage.py check --database default

# Run migrations
python3 manage.py migrate

# Create superuser
python3 manage.py createsuperuser

# Run server
python3 manage.py runserver
```

## Troubleshooting

### PostgreSQL Not Running

**macOS:**
```bash
# Check status
brew services list

# Start PostgreSQL
brew services start postgresql@14
```

**Docker:**
```bash
# Check if container is running
docker ps

# Start container
docker start postgres-shams
```

### Connection Refused

1. Check PostgreSQL is running
2. Verify port 5432 is not blocked
3. Check credentials in `.env` file

### Database Does Not Exist

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE shams_vision;

# Exit
\q
```

### Permission Denied

```bash
# Connect as superuser
psql -U postgres

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE shams_vision TO postgres;
```

## Next Steps

Once connection is successful:

1. ✅ Run migrations: `python3 manage.py migrate`
2. ✅ Create superuser: `python3 manage.py createsuperuser`
3. ✅ Test admin: `python3 manage.py runserver`
4. ✅ Access admin at: http://127.0.0.1:8000/admin/

