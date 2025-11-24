#!/bin/bash

# Test script for Rewards and Penalties APIs

BASE_URL="http://localhost:8000"
API_BASE="${BASE_URL}/api"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Testing Rewards & Penalties APIs"
echo "=========================================="
echo ""

# Login as Field Agent
echo -e "${YELLOW}1. Logging in as Field Agent...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "${API_BASE}/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_work_id": "fieldagent@example.com",
    "password": "password123"
  }')

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo -e "${RED}❌ Login failed. Please create a field agent user first.${NC}"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo -e "${GREEN}✅ Login successful${NC}"
echo ""

# Test Get User Points
echo -e "${YELLOW}2. Testing GET /api/finance/rewards/my-points/${NC}"
RESPONSE=$(curl -s -X GET "${API_BASE}/finance/rewards/my-points/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")
echo "$RESPONSE" | python3 -m json.tool
echo ""

# Test Get Rewards Activity
echo -e "${YELLOW}3. Testing GET /api/finance/rewards/activity/?period=this_month${NC}"
RESPONSE=$(curl -s -X GET "${API_BASE}/finance/rewards/activity/?period=this_month" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")
echo "$RESPONSE" | python3 -m json.tool
echo ""

# Test Get Rewards History
echo -e "${YELLOW}4. Testing GET /api/finance/rewards/history/?period=all_time${NC}"
RESPONSE=$(curl -s -X GET "${API_BASE}/finance/rewards/history/?period=all_time" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")
echo "$RESPONSE" | python3 -m json.tool
echo ""

# Test Get Penalties List
echo -e "${YELLOW}5. Testing GET /api/administration/penalties/?period=this_month${NC}"
RESPONSE=$(curl -s -X GET "${API_BASE}/administration/penalties/?period=this_month" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")
echo "$RESPONSE" | python3 -m json.tool
echo ""

# Test Get Penalties Summary
echo -e "${YELLOW}6. Testing GET /api/administration/penalties/summary/?period=all_time${NC}"
RESPONSE=$(curl -s -X GET "${API_BASE}/administration/penalties/summary/?period=all_time" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")
echo "$RESPONSE" | python3 -m json.tool
echo ""

echo -e "${GREEN}=========================================="
echo "All API tests completed!"
echo "==========================================${NC}"

