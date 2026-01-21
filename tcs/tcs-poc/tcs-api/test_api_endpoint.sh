#!/bin/bash

# Test the /new endpoint

echo "Testing /api/v1/trades/new endpoint..."
echo ""

# Test 1: Vanilla EUR IRS
echo "Test 1: Vanilla EUR IRS"
curl -X GET "http://localhost:8000/api/v1/trades/new?trade_type=irs&subtype=vanilla&currency=EUR&leg_types=fixed,floating-ibor" \
  -H "accept: application/json" | jq '.'

echo ""
echo "---"
echo ""

# Test 2: Check Swagger docs
echo "Swagger UI available at: http://localhost:8000/docs"
echo "ReDoc available at: http://localhost:8000/redoc"