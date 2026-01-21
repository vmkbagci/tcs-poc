#!/bin/bash

# Script to run full integration tests for TCS system
# This script starts both services and runs integration tests

set -e

echo "========================================="
echo "TCS Full Integration Test Runner"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if services are already running
check_service() {
    local url=$1
    local name=$2
    
    if curl -s -f "$url/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name is already running"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} $name is not running"
        return 1
    fi
}

# Function to start a service in background
start_service() {
    local dir=$1
    local script=$2
    local name=$3
    local port=$4
    
    echo "Starting $name on port $port..."
    cd "$dir"
    ./"$script" > /dev/null 2>&1 &
    local pid=$!
    cd - > /dev/null
    
    # Wait for service to be ready
    local max_wait=30
    local count=0
    while [ $count -lt $max_wait ]; do
        if curl -s -f "http://localhost:$port/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} $name started (PID: $pid)"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    
    echo -e "${RED}✗${NC} Failed to start $name"
    return 1
}

# Check current status
echo "Checking service status..."
API_RUNNING=false
STORE_RUNNING=false

if check_service "http://localhost:5000" "tcs-api"; then
    API_RUNNING=true
fi

if check_service "http://localhost:5500" "tcs-store"; then
    STORE_RUNNING=true
fi

echo ""

# Start services if needed
STARTED_API=false
STARTED_STORE=false

if [ "$STORE_RUNNING" = false ]; then
    if start_service "tcs-store" "run-store.sh" "tcs-store" "5500"; then
        STARTED_STORE=true
        sleep 2  # Give it a moment to fully initialize
    else
        echo -e "${RED}Failed to start tcs-store${NC}"
        exit 1
    fi
fi

if [ "$API_RUNNING" = false ]; then
    if start_service "tcs-api" "run-api.sh" "tcs-api" "5000"; then
        STARTED_API=true
        sleep 2  # Give it a moment to fully initialize
    else
        echo -e "${RED}Failed to start tcs-api${NC}"
        exit 1
    fi
fi

echo ""
echo "========================================="
echo "Running Integration Tests"
echo "========================================="
echo ""

# Run the integration tests
cd tcs-api
poetry run pytest tests/test_full_integration.py -v --tb=short

TEST_EXIT_CODE=$?

echo ""
echo "========================================="
echo "Test Results"
echo "========================================="

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All integration tests passed!${NC}"
else
    echo -e "${RED}✗ Some integration tests failed${NC}"
fi

# Cleanup: stop services we started
echo ""
if [ "$STARTED_API" = true ] || [ "$STARTED_STORE" = true ]; then
    echo "Cleaning up started services..."
    
    if [ "$STARTED_API" = true ]; then
        echo "Stopping tcs-api..."
        pkill -f "uvicorn.*trade_api" || true
    fi
    
    if [ "$STARTED_STORE" = true ]; then
        echo "Stopping tcs-store..."
        pkill -f "uvicorn.*tcs_store" || true
    fi
    
    echo -e "${GREEN}✓${NC} Cleanup complete"
fi

echo ""
exit $TEST_EXIT_CODE
