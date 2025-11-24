#!/bin/bash

BASE_URL="http://localhost:8000/api"

echo "============================================================"
echo "  SHAMS VISION API - COMPREHENSIVE ENDPOINT TESTING"
echo "============================================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_section() {
    echo ""
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

print_test() {
    if [ "$2" == "PASS" ]; then
        echo -e "${GREEN}✅ $1: PASS${NC}"
    elif [ "$2" == "FAIL" ]; then
        echo -e "${RED}❌ $1: FAIL${NC}"
        if [ -n "$3" ]; then
            echo "   $3"
        fi
    else
        echo -e "${YELLOW}⏭️  $1: SKIP${NC}"
        if [ -n "$3" ]; then
            echo "   $3"
        fi
    fi
}

# Test Authentication
print_section "AUTHENTICATION ENDPOINTS"

LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login/" \
    -H "Content-Type: application/json" \
    -d '{"work_id":"ADMIN001","password":"admin123"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    print_test "POST /api/auth/login/" "PASS" "Token received: ${TOKEN:0:20}..."
else
    print_test "POST /api/auth/login/" "FAIL" "Could not login"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

# Test Profile
PROFILE_RESPONSE=$(curl -s -X GET "$BASE_URL/auth/profile/" \
    -H "Authorization: Bearer $TOKEN")
if echo "$PROFILE_RESPONSE" | grep -q '"success"'; then
    print_test "GET /api/auth/profile/" "PASS"
else
    print_test "GET /api/auth/profile/" "FAIL" "Status check failed"
fi

# Test District Endpoints
print_section "DISTRICT ENDPOINTS"

# List districts
DISTRICTS_RESPONSE=$(curl -s -X GET "$BASE_URL/operations/districts/" \
    -H "Authorization: Bearer $TOKEN")
if echo "$DISTRICTS_RESPONSE" | grep -q '"results"\|"count"'; then
    COUNT=$(echo "$DISTRICTS_RESPONSE" | grep -o '"count":[0-9]*' | cut -d':' -f2)
    print_test "GET /api/operations/districts/" "PASS" "Found districts"
else
    print_test "GET /api/operations/districts/" "FAIL"
fi

# Create district
CREATE_DISTRICT_RESPONSE=$(curl -s -X POST "$BASE_URL/operations/districts/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Al Naseem Test",
        "code": "ALN_TEST",
        "priority": "HIGH",
        "status": "ACTIVE",
        "description": "Test district for API testing"
    }')

DISTRICT_ID=$(echo "$CREATE_DISTRICT_RESPONSE" | grep -o '"id":[0-9]*' | cut -d':' -f2)

if [ -n "$DISTRICT_ID" ]; then
    print_test "POST /api/operations/districts/" "PASS" "Created district ID: $DISTRICT_ID"
elif echo "$CREATE_DISTRICT_RESPONSE" | grep -q "already exists\|unique"; then
    print_test "POST /api/operations/districts/" "PASS" "District may already exist"
    # Get first district ID
    DISTRICT_ID=$(echo "$DISTRICTS_RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
else
    print_test "POST /api/operations/districts/" "FAIL" "Could not create district"
    DISTRICT_ID=""
fi

# Get district detail
if [ -n "$DISTRICT_ID" ]; then
    DISTRICT_DETAIL=$(curl -s -X GET "$BASE_URL/operations/districts/$DISTRICT_ID/" \
        -H "Authorization: Bearer $TOKEN")
    if echo "$DISTRICT_DETAIL" | grep -q '"id"'; then
        print_test "GET /api/operations/districts/$DISTRICT_ID/" "PASS"
    else
        print_test "GET /api/operations/districts/$DISTRICT_ID/" "FAIL"
    fi
    
    # Get stores in district
    STORES_RESPONSE=$(curl -s -X GET "$BASE_URL/operations/districts/$DISTRICT_ID/stores/" \
        -H "Authorization: Bearer $TOKEN")
    if echo "$STORES_RESPONSE" | grep -q '"success"'; then
        print_test "GET /api/operations/districts/$DISTRICT_ID/stores/" "PASS"
    else
        print_test "GET /api/operations/districts/$DISTRICT_ID/stores/" "FAIL"
    fi
fi

# Today's stats
TODAY_STATS=$(curl -s -X GET "$BASE_URL/operations/districts/today-stats/" \
    -H "Authorization: Bearer $TOKEN")
if echo "$TODAY_STATS" | grep -q '"success"'; then
    print_test "GET /api/operations/districts/today-stats/" "PASS"
else
    print_test "GET /api/operations/districts/today-stats/" "FAIL"
fi

# Test Store Visit Endpoints
print_section "STORE VISIT ENDPOINTS"

STORE_VISITS=$(curl -s -X GET "$BASE_URL/operations/store-visits/" \
    -H "Authorization: Bearer $TOKEN")
if echo "$STORE_VISITS" | grep -q '"results"\|"count"'; then
    print_test "GET /api/operations/store-visits/" "PASS"
else
    print_test "GET /api/operations/store-visits/" "FAIL"
fi

print_test "POST /api/operations/store-visits/" "SKIP" "Requires route and store setup"

# Test Work Session Endpoints
print_section "WORK SESSION ENDPOINTS"

CURRENT_SESSION=$(curl -s -X GET "$BASE_URL/operations/sessions/current/" \
    -H "Authorization: Bearer $TOKEN")
if echo "$CURRENT_SESSION" | grep -q '"success"'; then
    print_test "GET /api/operations/sessions/current/" "PASS"
else
    print_test "GET /api/operations/sessions/current/" "FAIL"
fi

# Test Leave Endpoints
print_section "LEAVE REQUEST ENDPOINTS"

LEAVES=$(curl -s -X GET "$BASE_URL/leaves/" \
    -H "Authorization: Bearer $TOKEN")
if echo "$LEAVES" | grep -q '"results"\|"count"'; then
    print_test "GET /api/leaves/" "PASS"
else
    print_test "GET /api/leaves/" "FAIL"
fi

# Test File Endpoints
print_section "FILE MANAGEMENT ENDPOINTS"

FILES=$(curl -s -X GET "$BASE_URL/files/" \
    -H "Authorization: Bearer $TOKEN")
if echo "$FILES" | grep -q '"results"\|"count"'; then
    print_test "GET /api/files/" "PASS"
else
    print_test "GET /api/files/" "FAIL"
fi

# Test User Endpoints
print_section "USER MANAGEMENT ENDPOINTS"

USERS=$(curl -s -X GET "$BASE_URL/auth/users/" \
    -H "Authorization: Bearer $TOKEN")
if echo "$USERS" | grep -q '"results"\|"count"'; then
    print_test "GET /api/auth/users/" "PASS"
else
    print_test "GET /api/auth/users/" "FAIL"
fi

# Summary
print_section "TEST SUMMARY"
echo -e "${GREEN}✅ All endpoint tests completed!${NC}"
echo ""
echo "Note: Some endpoints may require additional setup (routes, stores, etc.)"
echo "      to fully test create/update operations."

