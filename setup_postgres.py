#!/usr/bin/env python3
"""
Script to test PostgreSQL connection and create database if needed.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shams_vision.settings')
django.setup()

from django.db import connection
from django.conf import settings


def test_connection():
    """Test PostgreSQL connection."""
    print("=" * 60)
    print("Testing PostgreSQL Connection...")
    print("=" * 60)
    
    db_config = settings.DATABASES['default']
    print(f"\nDatabase Configuration:")
    print(f"  Engine: {db_config['ENGINE']}")
    print(f"  Name: {db_config['NAME']}")
    print(f"  User: {db_config['USER']}")
    print(f"  Host: {db_config['HOST']}")
    print(f"  Port: {db_config['PORT']}")
    
    try:
        # Test connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"\n✅ Connection Successful!")
            print(f"PostgreSQL Version: {version}")
            
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", [db_config['NAME']])
            exists = cursor.fetchone()
            
            if exists:
                print(f"✅ Database '{db_config['NAME']}' exists")
            else:
                print(f"⚠️  Database '{db_config['NAME']}' does not exist")
                print(f"   Create it with: CREATE DATABASE {db_config['NAME']};")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Connection Failed!")
        print(f"Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check if PostgreSQL is running")
        print("2. Verify database credentials in .env file")
        print("3. Ensure database exists: CREATE DATABASE shams_vision;")
        return False


if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)

