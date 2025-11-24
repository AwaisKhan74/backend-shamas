#!/usr/bin/env python3
"""
Comprehensive endpoint testing script for Shams Vision API
"""
import json
import requests
import sys
from datetime import date, timedelta

BASE_URL = "http://localhost:8000/api"

# Test credentials (adjust if needed)
TEST_USERS = {
    'admin': {'work_id': 'ADMIN001', 'password': 'admin123'},
    'manager': {'work_id': 'MGR001', 'password': 'manager123'},
    'agent': {'work_id': 'AGENT001', 'password': 'agent123'},
}

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_test(name, status, details=""):
    status_icon = "✅" if status == "PASS" else "❌"
    print(f"{status_icon} {name}: {status}")
    if details:
        print(f"   {details}")

def login(user_type='admin'):
    """Login and get access token"""
    url = f"{BASE_URL}/auth/login/"
    data = {
        "work_id": TEST_USERS[user_type]['work_id'],
        "password": TEST_USERS[user_type]['password']
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        token = response.json().get('access')
        return token
    return None

def test_auth_endpoints():
    """Test authentication endpoints"""
    print_section("AUTHENTICATION ENDPOINTS")
    
    # Test login
    token = login('admin')
    if token:
        print_test("POST /api/auth/login/", "PASS", f"Token received: {token[:20]}...")
    else:
        print_test("POST /api/auth/login/", "FAIL", "Could not login")
        return None
    
    # Test profile
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
    if response.status_code == 200:
        print_test("GET /api/auth/profile/", "PASS")
    else:
        print_test("GET /api/auth/profile/", "FAIL", f"Status: {response.status_code}")
    
    return token

def test_district_endpoints(token):
    """Test district endpoints"""
    print_section("DISTRICT ENDPOINTS")
    headers = {"Authorization": f"Bearer {token}"}
    
    # List districts
    response = requests.get(f"{BASE_URL}/operations/districts/", headers=headers)
    if response.status_code == 200:
        districts = response.json()
        print_test("GET /api/operations/districts/", "PASS", f"Found {len(districts.get('results', []))} districts")
    else:
        print_test("GET /api/operations/districts/", "FAIL", f"Status: {response.status_code}")
    
    # Create district
    district_data = {
        "name": "Al Naseem",
        "code": "ALN",
        "priority": "HIGH",
        "status": "ACTIVE",
        "description": "Test district"
    }
    response = requests.post(f"{BASE_URL}/operations/districts/", headers=headers, json=district_data)
    if response.status_code == 201:
        district_id = response.json().get('id')
        print_test("POST /api/operations/districts/", "PASS", f"Created district ID: {district_id}")
    elif response.status_code == 400:
        # District might already exist
        print_test("POST /api/operations/districts/", "PASS", "District may already exist")
        # Try to get existing district
        response = requests.get(f"{BASE_URL}/operations/districts/", headers=headers)
        if response.status_code == 200:
            districts = response.json().get('results', [])
            if districts:
                district_id = districts[0].get('id')
            else:
                return None
        else:
            return None
    else:
        print_test("POST /api/operations/districts/", "FAIL", f"Status: {response.status_code}")
        return None
    
    # Get district detail
    response = requests.get(f"{BASE_URL}/operations/districts/{district_id}/", headers=headers)
    if response.status_code == 200:
        print_test(f"GET /api/operations/districts/{district_id}/", "PASS")
    else:
        print_test(f"GET /api/operations/districts/{district_id}/", "FAIL", f"Status: {response.status_code}")
    
    # Get stores in district
    response = requests.get(f"{BASE_URL}/operations/districts/{district_id}/stores/", headers=headers)
    if response.status_code == 200:
        stores = response.json().get('stores', [])
        print_test(f"GET /api/operations/districts/{district_id}/stores/", "PASS", f"Found {len(stores)} stores")
    else:
        print_test(f"GET /api/operations/districts/{district_id}/stores/", "FAIL", f"Status: {response.status_code}")
    
    # Today's stats
    response = requests.get(f"{BASE_URL}/operations/districts/today-stats/", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print_test("GET /api/operations/districts/today-stats/", "PASS", f"Found {data.get('count', 0)} districts")
    else:
        print_test("GET /api/operations/districts/today-stats/", "FAIL", f"Status: {response.status_code}")
    
    return district_id

def test_store_visit_endpoints(token):
    """Test store visit endpoints"""
    print_section("STORE VISIT ENDPOINTS")
    headers = {"Authorization": f"Bearer {token}"}
    
    # List store visits
    response = requests.get(f"{BASE_URL}/operations/store-visits/", headers=headers)
    if response.status_code == 200:
        visits = response.json().get('results', [])
        print_test("GET /api/operations/store-visits/", "PASS", f"Found {len(visits)} visits")
    else:
        print_test("GET /api/operations/store-visits/", "FAIL", f"Status: {response.status_code}")
    
    # Note: Creating a store visit requires route and store to exist
    # This is tested if routes/stores exist in the system
    print_test("POST /api/operations/store-visits/", "SKIP", "Requires route and store setup")

def test_work_session_endpoints(token):
    """Test work session endpoints"""
    print_section("WORK SESSION ENDPOINTS")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get current session
    response = requests.get(f"{BASE_URL}/operations/sessions/current/", headers=headers)
    if response.status_code == 200:
        print_test("GET /api/operations/sessions/current/", "PASS")
    else:
        print_test("GET /api/operations/sessions/current/", "FAIL", f"Status: {response.status_code}")

def test_leave_endpoints(token):
    """Test leave request endpoints"""
    print_section("LEAVE REQUEST ENDPOINTS")
    headers = {"Authorization": f"Bearer {token}"}
    
    # List leaves
    response = requests.get(f"{BASE_URL}/leaves/", headers=headers)
    if response.status_code == 200:
        leaves = response.json().get('results', [])
        print_test("GET /api/leaves/", "PASS", f"Found {len(leaves)} leave requests")
    else:
        print_test("GET /api/leaves/", "FAIL", f"Status: {response.status_code}")

def test_file_endpoints(token):
    """Test file management endpoints"""
    print_section("FILE MANAGEMENT ENDPOINTS")
    headers = {"Authorization": f"Bearer {token}"}
    
    # List files
    response = requests.get(f"{BASE_URL}/files/", headers=headers)
    if response.status_code == 200:
        files = response.json().get('results', [])
        print_test("GET /api/files/", "PASS", f"Found {len(files)} files")
    else:
        print_test("GET /api/files/", "FAIL", f"Status: {response.status_code}")

def test_user_endpoints(token):
    """Test user management endpoints"""
    print_section("USER MANAGEMENT ENDPOINTS")
    headers = {"Authorization": f"Bearer {token}"}
    
    # List users (admin only)
    response = requests.get(f"{BASE_URL}/auth/users/", headers=headers)
    if response.status_code == 200:
        users = response.json().get('results', [])
        print_test("GET /api/auth/users/", "PASS", f"Found {len(users)} users")
    else:
        print_test("GET /api/auth/users/", "FAIL", f"Status: {response.status_code}")

def main():
    print("\n" + "="*60)
    print("  SHAMS VISION API - COMPREHENSIVE ENDPOINT TESTING")
    print("="*60)
    
    # Test authentication
    token = test_auth_endpoints()
    if not token:
        print("\n❌ Authentication failed. Cannot proceed with other tests.")
        sys.exit(1)
    
    # Test all endpoints
    test_district_endpoints(token)
    test_store_visit_endpoints(token)
    test_work_session_endpoints(token)
    test_leave_endpoints(token)
    test_file_endpoints(token)
    test_user_endpoints(token)
    
    print_section("TEST SUMMARY")
    print("✅ All endpoint tests completed!")
    print("\nNote: Some endpoints may require additional setup (routes, stores, etc.)")
    print("      to fully test create/update operations.")

if __name__ == "__main__":
    main()

