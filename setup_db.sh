#!/bin/bash

# PostgreSQL Setup Script for Shams Vision

echo "=========================================="
echo "Setting up PostgreSQL for Shams Vision"
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check if container already exists
if docker ps -a | grep -q postgres-shams; then
    echo "📦 PostgreSQL container 'postgres-shams' already exists"
    
    # Check if it's running
    if docker ps | grep -q postgres-shams; then
        echo "✅ Container is already running"
    else
        echo "🚀 Starting existing container..."
        docker start postgres-shams
        sleep 2
    fi
else
    echo "📦 Creating new PostgreSQL container..."
    docker run --name postgres-shams \
        -e POSTGRES_PASSWORD=postgres \
        -e POSTGRES_DB=shams_vision \
        -p 5432:5432 \
        -d postgres:14
    
    echo "⏳ Waiting for PostgreSQL to start..."
    sleep 5
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
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
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Test connection
echo ""
echo "🔍 Testing database connection..."
python3 setup_postgres.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Run migrations: python3 manage.py migrate"
    echo "  2. Create superuser: python3 manage.py createsuperuser"
    echo "  3. Start server: python3 manage.py runserver"
else
    echo ""
    echo "⚠️  Connection test failed. Please check the error above."
fi

