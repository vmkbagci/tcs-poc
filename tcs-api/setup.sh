#!/bin/bash

# Trade API Quick Setup Script for Debian/Ubuntu
# This script automates the installation process described in DEPLOYMENT_GUIDE.md

set -e  # Exit on any error

echo "🚀 Trade API Quick Setup Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Step 1: Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Step 2: Install essential dependencies
print_status "Installing essential build tools and dependencies..."
sudo apt install -y \
    curl \
    wget \
    git \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    ca-certificates \
    gnupg \
    lsb-release

# Step 3: Check Python version
print_status "Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 10 ]]; then
    print_warning "Python version $PYTHON_VERSION detected. Python 3.10+ is recommended."
    print_warning "Consider upgrading Python or the setup may fail."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    print_status "Python $PYTHON_VERSION detected - compatible ✓"
fi

# Step 4: Install Poetry
print_status "Installing Poetry..."
if command -v poetry &> /dev/null; then
    print_status "Poetry already installed: $(poetry --version)"
else
    curl -sSL https://install.python-poetry.org | python3 -
    
    # Add Poetry to PATH
    export PATH="$HOME/.local/bin:$PATH"
    
    # Add to bashrc if not already there
    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        print_status "Added Poetry to PATH in ~/.bashrc"
    fi
    
    # Verify installation
    if command -v poetry &> /dev/null; then
        print_status "Poetry installed successfully: $(poetry --version)"
    else
        print_error "Poetry installation failed"
        exit 1
    fi
fi

# Step 5: Install project dependencies
print_status "Installing project dependencies..."
if [[ -f "pyproject.toml" ]]; then
    poetry install
    print_status "Dependencies installed successfully ✓"
else
    print_error "pyproject.toml not found. Are you in the correct directory?"
    exit 1
fi

# Step 6: Verify template directory
print_status "Verifying template directory structure..."
if [[ -d "templates/v1" ]]; then
    TEMPLATE_COUNT=$(find templates/v1 -name "*.json" | wc -l)
    print_status "Found $TEMPLATE_COUNT template files in templates/v1/ ✓"
else
    print_error "templates/v1 directory not found. Template system will not work."
    exit 1
fi

# Step 7: Setup environment
print_status "Setting up environment configuration..."
if [[ ! -f ".env" ]]; then
    if [[ -f ".env.example" ]]; then
        cp .env.example .env
        print_status "Created .env from .env.example"
    else
        print_warning ".env.example not found, creating basic .env"
        cat > .env << EOF
TRADE_API_DEBUG=true
TRADE_API_HOST=0.0.0.0
TRADE_API_PORT=8000
TRADE_API_MAX_TRADES_IN_MEMORY=10000
EOF
    fi
else
    print_status ".env already exists, skipping creation"
fi

# Step 8: Run tests
print_status "Running tests to verify installation..."
if poetry run pytest tests/test_setup.py -v; then
    print_status "All tests passed ✓"
else
    print_warning "Some tests failed. This may be expected if features are still in development."
    print_warning "Check the output above for details."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 9: Test application startup and /new endpoint
print_status "Testing application startup..."
if poetry run python -c "from trade_api.main import app; print('FastAPI app created successfully')"; then
    print_status "Application startup test passed ✓"
else
    print_error "Application startup test failed"
    exit 1
fi

print_status "Testing /new endpoint..."
if poetry run python -c "
from fastapi.testclient import TestClient
from trade_api.main import app
client = TestClient(app)
response = client.get('/api/v1/trades/new?trade_type=irswap&trade_subtype=vanilla')
assert response.status_code == 200, f'Expected 200, got {response.status_code}'
assert response.json()['success'] is True, 'Expected success=True'
print('GET /api/v1/trades/new endpoint working ✓')
"; then
    print_status "/new endpoint test passed ✓"
else
    print_error "/new endpoint test failed"
    exit 1
fi

# Final instructions
echo
echo "🎉 Setup completed successfully!"
echo "================================"
echo
echo "To start the development server:"
echo "  poetry run uvicorn trade_api.main:app --host 0.0.0.0 --port 8000 --reload"
echo
echo "To start the production server:"
echo "  poetry run gunicorn trade_api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"
echo
echo "API will be available at:"
echo "  - Local: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Network: http://$(hostname -I | awk '{print $1}'):8000"
echo
echo "For more details, see DEPLOYMENT_GUIDE.md"