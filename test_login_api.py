#!/usr/bin/env python3
"""
Test script for Login API.
"""
import json
import sys

try:
    import requests
except ImportError:  # pragma: no cover - optional dependency for manual script
    requests = None
    sys.stderr.write(
        "[test_login_api] 'requests' package not installed. Install it with 'pip install requests' "
        "to run this manual API smoke test.\n"
    )

BASE_URL = 'http://127.0.0.1:8000/api/auth'


def test_login():
    """Test login API."""
    if requests is None:
        raise RuntimeError("'requests' is required to run this script.")

    print("=" * 60)
    print("Testing Login API")
    print("=" * 60)
    
    # Create session
    session = requests.Session()
    
    # Test 1: Login with work_id
    print("\n1. Testing login with work_id...")
    response = session.post(f'{BASE_URL}/login/', json={
        'work_id': 'ADMIN001',
        'password': 'admin123'
    })
    
    print(f"   Status Code: {response.status_code}")
    login_data = response.json()
    print(f"   Response: {json.dumps(login_data, indent=2)}")
    
    if response.status_code == 200:
        print("   ✅ Login successful!")
        session.headers.update({
            'Authorization': f"Bearer {login_data['access_token']}",
            'Content-Type': 'application/json'
        })
        
        # Test 2: Get current user
        print("\n2. Testing get current user...")
        response = session.get(f'{BASE_URL}/profile/')
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("   ✅ Get current user successful!")
        
        # Test 3: Logout
        print("\n3. Testing logout...")
        response = session.post(f'{BASE_URL}/token/blacklist/', json={
            'refresh': login_data.get('refresh_token', '')
        })
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text or '{}'}")
        
        if response.status_code in (200, 205):
            print("   ✅ Logout successful!")
    else:
        print("   ❌ Login failed!")
    
    # Test 4: Login with email
    print("\n4. Testing login with email...")
    session2 = requests.Session()
    response = session2.post(f'{BASE_URL}/login/', json={
        'email': 'admin@shamsvision.com',
        'password': 'admin123'
    })
    
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Login with email successful!")
    else:
        print(f"   ❌ Login failed: {response.json()}")
    
    # Test 5: Invalid credentials
    print("\n5. Testing invalid credentials...")
    response = requests.post(f'{BASE_URL}/login/', json={
        'work_id': 'ADMIN001',
        'password': 'wrongpassword'
    })
    
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 400:
        print("   ✅ Invalid credentials handled correctly!")
    else:
        print(f"   ❌ Unexpected response: {response.json()}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == '__main__':
    if requests is None:
        sys.exit("Install the 'requests' package to run this script.")

    try:
        test_login()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server.")
        print("   Make sure the server is running: python3 manage.py runserver")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


