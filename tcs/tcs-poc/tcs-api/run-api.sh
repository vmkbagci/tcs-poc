#!/usr/bin/env bash

###############################################################################
# Trade API - Poetry Runner Script
#
# This script starts the Trade API using Poetry with configurable options
# for both development and production environments.
#
# Usage:
#   ./run-api.sh [mode]
#
# Modes:
#   dev       - Development mode with auto-reload (default)
#   prod      - Production mode with Gunicorn workers
#   test      - Run tests before starting server
#   help      - Show this help message
#
# Requirements:
#   - Poetry installed and in PATH
#   - Dependencies installed (poetry install)
#   - .env file configured (copy from .env.example)
###############################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
MODE="${1:-dev}"
HOST="${TRADE_API_HOST:-0.0.0.0}"
PORT="${TRADE_API_PORT:-5000}"
WORKERS="${TRADE_API_WORKERS:-4}"

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Trade API - FastAPI Application${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

show_help() {
    cat << EOF
Trade API - Poetry Runner Script

USAGE:
    ./run-api.sh [mode]

MODES:
    dev       Development mode with auto-reload (default)
    prod      Production mode with Gunicorn workers
    test      Run tests before starting server
    help      Show this help message

EXAMPLES:
    ./run-api.sh              # Start in development mode
    ./run-api.sh dev          # Start in development mode
    ./run-api.sh prod         # Start in production mode
    ./run-api.sh test         # Run tests then start

ENVIRONMENT VARIABLES:
    TRADE_API_HOST            Host to bind to (default: 0.0.0.0)
    TRADE_API_PORT            Port to bind to (default: 8000)
    TRADE_API_WORKERS         Number of worker processes (default: 4, prod only)
    TRADE_API_DEBUG           Enable debug mode (default: true)

CONFIGURATION:
    Edit .env file to customize settings
    Copy from .env.example if not exists

For more information, see README.md and DEPLOYMENT_GUIDE.md
EOF
}

check_poetry() {
    if ! command -v poetry &> /dev/null; then
        print_error "Poetry is not installed or not in PATH"
        echo
        echo "Install Poetry with:"
        echo "  curl -sSL https://install.python-poetry.org | python3 -"
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo
        exit 1
    fi
    print_success "Poetry found: $(poetry --version)"
}

check_dependencies() {
    if [ ! -f "pyproject.toml" ]; then
        print_error "pyproject.toml not found. Are you in the tcs-api directory?"
        exit 1
    fi

    # Check if virtual environment exists
    if ! poetry env info &> /dev/null; then
        print_warning "Virtual environment not found. Installing dependencies..."
        poetry install
    else
        print_success "Virtual environment found"
    fi
}

check_env_file() {
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_warning ".env file not found. Copying from .env.example..."
            cp .env.example .env
            print_success ".env file created"
        else
            print_warning ".env file not found. Using default configuration."
        fi
    else
        print_success ".env file found"
    fi
}

run_tests() {
    print_info "Running tests..."
    echo
    if poetry run pytest tests/test_setup.py -v; then
        print_success "All tests passed"
        echo
    else
        print_error "Tests failed"
        exit 1
    fi
}

start_dev_server() {
    print_info "Starting development server..."
    print_info "Mode: Development with auto-reload"
    print_info "Host: $HOST"
    print_info "Port: $PORT"
    echo
    print_success "API will be available at:"
    echo "  - Local:   http://localhost:$PORT"
    echo "  - Network: http://$HOST:$PORT"
    echo "  - API Docs: http://localhost:$PORT/docs"
    echo
    print_info "Press Ctrl+C to stop the server"
    echo

    # Start Uvicorn with auto-reload
    poetry run uvicorn trade_api.main:app \
        --host "$HOST" \
        --port "$PORT" \
        --reload
}

start_prod_server() {
    print_info "Starting production server..."
    print_info "Mode: Production with Gunicorn"
    print_info "Host: $HOST"
    print_info "Port: $PORT"
    print_info "Workers: $WORKERS"
    echo
    print_success "API will be available at:"
    echo "  - Local:   http://localhost:$PORT"
    echo "  - Network: http://$HOST:$PORT"
    echo "  - API Docs: http://localhost:$PORT/docs (if debug enabled)"
    echo
    print_info "Press Ctrl+C to stop the server"
    echo

    # Start Gunicorn with Uvicorn workers
    poetry run gunicorn trade_api.main:app \
        --workers "$WORKERS" \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind "$HOST:$PORT" \
        --access-logfile - \
        --error-logfile -
}

###############################################################################
# Main Script
###############################################################################

print_header

# Handle help command
if [ "$MODE" = "help" ] || [ "$MODE" = "-h" ] || [ "$MODE" = "--help" ]; then
    show_help
    exit 0
fi

# Verify prerequisites
print_info "Checking prerequisites..."
check_poetry
check_dependencies
check_env_file
echo

# Handle different modes
case "$MODE" in
    dev|development)
        start_dev_server
        ;;

    prod|production)
        start_prod_server
        ;;

    test)
        run_tests
        print_info "Tests completed. Starting development server..."
        echo
        start_dev_server
        ;;

    *)
        print_error "Unknown mode: $MODE"
        echo
        echo "Valid modes: dev, prod, test, help"
        echo "Run './run-api.sh help' for more information"
        exit 1
        ;;
esac