#!/bin/bash

# Trade API Docker Quick Setup Script
# This script sets up the Trade API using Docker for easy deployment

set -e  # Exit on any error

echo "🐳 Trade API Docker Setup Script"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if Docker is installed
print_step "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first:"
    echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "  sudo sh get-docker.sh"
    echo "  sudo usermod -aG docker \$USER"
    echo "  # Log out and back in, then run this script again"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not available. Please install Docker Compose:"
    echo "  sudo apt install docker-compose-plugin"
    exit 1
fi

print_status "Docker is installed and ready ✓"

# Check if user is in docker group
if ! groups $USER | grep -q docker; then
    print_warning "User $USER is not in the docker group."
    print_warning "You may need to run docker commands with sudo, or add yourself to the docker group:"
    echo "  sudo usermod -aG docker $USER"
    echo "  # Then log out and back in"
fi

# Create logs directory
print_step "Creating logs directory..."
mkdir -p logs

# Build the Docker image
print_step "Building Docker image..."
docker build -t trade-api:latest .

if [ $? -eq 0 ]; then
    print_status "Docker image built successfully ✓"
else
    print_error "Docker image build failed"
    exit 1
fi

# Ask user for deployment option
echo
echo "Choose deployment option:"
echo "1) Simple Docker run (single container)"
echo "2) Docker Compose (recommended)"
echo "3) Docker Compose with nginx reverse proxy"
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        print_step "Starting Trade API with simple Docker run..."
        docker run -d \
            --name trade-api-container \
            -p 8000:8000 \
            -v $(pwd)/logs:/app/logs \
            -e TRADE_API_DEBUG=false \
            -e TRADE_API_HOST=0.0.0.0 \
            -e TRADE_API_PORT=8000 \
            trade-api:latest
        
        if [ $? -eq 0 ]; then
            print_status "Container started successfully ✓"
            echo "API available at: http://localhost:8000"
            echo "API docs at: http://localhost:8000/docs"
        else
            print_error "Failed to start container"
            exit 1
        fi
        ;;
    
    2)
        print_step "Starting Trade API with Docker Compose..."
        if command -v docker-compose &> /dev/null; then
            docker-compose up -d
        else
            docker compose up -d
        fi
        
        if [ $? -eq 0 ]; then
            print_status "Services started successfully ✓"
            echo "API available at: http://localhost:8000"
            echo "API docs at: http://localhost:8000/docs"
        else
            print_error "Failed to start services"
            exit 1
        fi
        ;;
    
    3)
        print_step "Starting Trade API with Docker Compose and nginx..."
        if command -v docker-compose &> /dev/null; then
            docker-compose --profile with-nginx up -d
        else
            docker compose --profile with-nginx up -d
        fi
        
        if [ $? -eq 0 ]; then
            print_status "Services started successfully ✓"
            echo "API available at: http://localhost (port 80)"
            echo "API docs at: http://localhost/docs"
            echo "Direct API access: http://localhost:8000"
        else
            print_error "Failed to start services"
            exit 1
        fi
        ;;
    
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

# Wait a moment for services to start
print_step "Waiting for services to start..."
sleep 10

# Test the API
print_step "Testing API health..."
if curl -s -X POST "http://localhost:8000/api/v1/trades/new" \
   -H "Content-Type: application/json" \
   -d '{"trade_type": "InterestRateSwap"}' > /dev/null; then
    print_status "API health check passed ✓"
else
    print_warning "API health check failed. The service might still be starting up."
    print_warning "Check logs with: docker logs trade-api-container"
fi

# Show running containers
print_step "Running containers:"
docker ps --filter "name=trade-api"

echo
echo "🎉 Docker setup completed!"
echo "=========================="
echo
echo "Useful commands:"
echo "  View logs:     docker logs trade-api-container -f"
echo "  Stop service:  docker stop trade-api-container"
echo "  Start service: docker start trade-api-container"
echo "  Remove all:    docker-compose down --volumes"
echo
echo "API Endpoints:"
echo "  POST /api/v1/trades/new      - Create new trade"
echo "  POST /api/v1/trades/save     - Save trade data"
echo "  POST /api/v1/trades/validate - Validate trade"
echo
echo "For more details, see DEPLOYMENT_GUIDE.md"