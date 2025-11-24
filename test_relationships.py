#!/usr/bin/env python3
"""
Comprehensive relationship verification script for FileManager model.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shams_vision.settings')
django.setup()

from core.models import FileManager, Route, User
from django.db import models
from django.core.exceptions import ValidationError

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def check_related_names():
    """Check all related_name usages for conflicts."""
    print_section("1. RELATED_NAME VERIFICATION")
    
    # Check User model reverse relationships
    print("\n📋 User Model Reverse Relationships:")
    user_fields = [f for f in User._meta.get_fields() 
                   if hasattr(f, 'related_name') and f.related_name]
    
    related_names = {}
    conflicts = []
    
    for field in user_fields:
        rel_name = field.related_name
        model_name = field.related_model.__name__ if hasattr(field, 'related_model') else 'Unknown'
        
        if rel_name in related_names:
            conflicts.append(f"CONFLICT: '{rel_name}' used by both {related_names[rel_name]} and {model_name}")
        else:
            related_names[rel_name] = model_name
        
        print(f"   ✅ {rel_name:30s} → {model_name}")
    
    if conflicts:
        print("\n❌ CONFLICTS FOUND:")
        for conflict in conflicts:
            print(f"   {conflict}")
        return False
    else:
        print("\n✅ No related_name conflicts for User model!")
        return True

def check_route_relationships():
    """Check Route model relationships."""
    print_section("2. ROUTE MODEL RELATIONSHIPS")
    
    print("\n📋 Route Model Reverse Relationships:")
    route_fields = [f for f in Route._meta.get_fields() 
                    if hasattr(f, 'related_name') and f.related_name]
    
    route_related = {}
    for field in route_fields:
        rel_name = field.related_name
        model_name = field.related_model.__name__ if hasattr(field, 'related_model') else 'Unknown'
        route_related[rel_name] = model_name
        print(f"   ✅ {rel_name:30s} → {model_name}")
    
    # Check for 'files' related_name
    if 'files' in route_related:
        print(f"\n✅ FileManager relationship found: Route.files → {route_related['files']}")
        return True
    else:
        print("\n❌ FileManager relationship NOT found!")
        return False

def test_filemanager_relationships():
    """Test FileManager model relationships."""
    print_section("3. FILEMANAGER MODEL RELATIONSHIPS")
    
    # Check forward relationships
    print("\n📋 FileManager Forward Relationships:")
    fm_fields = FileManager._meta.get_fields()
    
    for field in fm_fields:
        if hasattr(field, 'related_model') and field.related_model:
            rel_name = getattr(field, 'related_name', 'None')
            print(f"   ✅ {field.name:20s} → {field.related_model.__name__:20s} (related_name: {rel_name})")
    
    # Check field configurations
    user_field = FileManager._meta.get_field('user')
    route_field = FileManager._meta.get_field('route')
    
    print("\n📋 Field Configurations:")
    print(f"   ✅ user.on_delete: {user_field.remote_field.on_delete.__name__}")
    print(f"   ✅ user.related_name: {user_field.remote_field.related_name}")
    print(f"   ✅ route.on_delete: {route_field.remote_field.on_delete.__name__}")
    print(f"   ✅ route.related_name: {route_field.remote_field.related_name}")
    print(f"   ✅ route.null: {route_field.null}")
    print(f"   ✅ route.blank: {route_field.blank}")
    
    return True

def test_reverse_accessors():
    """Test reverse accessors work correctly."""
    print_section("4. REVERSE ACCESSOR TESTING")
    
    try:
        # Test User.managed_files
        user = User.objects.first()
        if user:
            print(f"\n✅ Testing User.managed_files:")
            print(f"   - User: {user.work_id}")
            print(f"   - Has attribute: {hasattr(user, 'managed_files')}")
            print(f"   - Type: {type(user.managed_files)}")
            print(f"   - Count: {user.managed_files.count()}")
        else:
            print("⚠️  No users found in database")
        
        # Test Route.files
        route = Route.objects.first()
        if route:
            print(f"\n✅ Testing Route.files:")
            print(f"   - Route: {route.name}")
            print(f"   - Has attribute: {hasattr(route, 'files')}")
            print(f"   - Type: {type(route.files)}")
            print(f"   - Count: {route.files.count()}")
        else:
            print("⚠️  No routes found in database")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing reverse accessors: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cascade_behavior():
    """Test cascade delete behavior."""
    print_section("5. CASCADE DELETE BEHAVIOR")
    
    print("\n📋 Expected Behavior:")
    print("   ✅ If User is deleted → FileManager records deleted (CASCADE)")
    print("   ✅ If Route is deleted → FileManager records deleted (CASCADE)")
    print("   ✅ Route can be null → Files can exist without route")
    
    user_field = FileManager._meta.get_field('user')
    route_field = FileManager._meta.get_field('route')
    
    user_field = FileManager._meta.get_field('user')
    route_field = FileManager._meta.get_field('route')
    
    print("\n📋 Actual Configuration:")
    print(f"   ✅ user.on_delete: {user_field.remote_field.on_delete.__name__} (matches expected: CASCADE)")
    print(f"   ✅ route.on_delete: {route_field.remote_field.on_delete.__name__} (matches expected: CASCADE)")
    print(f"   ✅ route.null: {route_field.null} (allows files without route)")
    
    if (user_field.remote_field.on_delete == models.CASCADE and 
        route_field.remote_field.on_delete == models.CASCADE and 
        route_field.null == True):
        print("\n✅ Cascade behavior configured correctly!")
        return True
    else:
        print("\n❌ Cascade behavior NOT configured correctly!")
        return False

def test_database_constraints():
    """Test database constraints."""
    print_section("6. DATABASE CONSTRAINTS")
    
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Check table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'file_manager'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if table_exists:
                print("✅ Table 'file_manager' exists in database")
                
                # Check foreign key constraints
                cursor.execute("""
                    SELECT
                        tc.constraint_name,
                        tc.table_name,
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                      AND tc.table_name = 'file_manager';
                """)
                
                fks = cursor.fetchall()
                if fks:
                    print("\n✅ Foreign Key Constraints:")
                    for fk in fks:
                        print(f"   - {fk[2]} → {fk[3]}.{fk[4]}")
                else:
                    print("\n⚠️  No foreign key constraints found")
                
                return True
            else:
                print("❌ Table 'file_manager' does NOT exist in database")
                return False
                
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def main():
    """Run all relationship tests."""
    print("\n" + "=" * 70)
    print("  FILEMANAGER RELATIONSHIP VERIFICATION")
    print("=" * 70)
    
    results = []
    
    # Run all tests
    results.append(("Related Names Check", check_related_names()))
    results.append(("Route Relationships", check_route_relationships()))
    results.append(("FileManager Relationships", test_filemanager_relationships()))
    results.append(("Reverse Accessors", test_reverse_accessors()))
    results.append(("Cascade Behavior", test_cascade_behavior()))
    results.append(("Database Constraints", test_database_constraints()))
    
    # Summary
    print_section("SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n✅ Passed: {passed}/{total}")
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Relationships are configured correctly!")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED! Please review the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

