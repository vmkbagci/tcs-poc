# Trade API Deployment Guide

## Setting up Trade API on Base Debian Image

This guide provides step-by-step instructions for setting up the Trade API project on a fresh Debian-based system (Ubuntu, Debian, etc.).

### Prerequisites

- Base Debian/Ubuntu system with sudo access
- Internet connection for package downloads
- Basic familiarity with command line

### System Requirements

- **Python**: 3.10+ (this guide tested with Python 3.13.10)
- **Memory**: Minimum 512MB RAM (1GB+ recommended)
- **Disk**: At least 500MB free space for dependencies
- **Network**: Internet access for package installation

## Step-by-Step Installation

### Step 1: Update System Packages

```bash
# Update package lists and upgrade system
sudo apt update && sudo apt upgrade -y

# Install essential build tools and dependencies
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
```

### Step 2: Verify Python Installation

```bash
# Check Python version (should be 3.10+)
python3 --version

# If Python version is less than 3.10, you may need to install a newer version
# For Ubuntu 20.04 or older, add deadsnakes PPA:
# sudo apt install software-properties-common
# sudo add-apt-repository ppa:deadsnakes/ppa
# sudo apt update
# sudo apt install python3.11 python3.11-venv python3.11-dev
```

### Step 3: Install Poetry (Python Dependency Manager)

```bash
# Install Poetry using the official installer
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH for current session
export PATH="$HOME/.local/bin:$PATH"

# Add Poetry to PATH permanently
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify Poetry installation
poetry --version
```

### Step 4: Clone and Setup Project

```bash
# Navigate to your desired project directory
cd /opt  # or ~/projects, or wherever you prefer

# Clone the project (replace with your actual repository URL)
# git clone <your-repo-url>
# cd <your-repo-name>/tcs-api

# Or if you have the project files locally, navigate to the tcs-api directory
cd tcs-api

# Verify project structure
ls -la
```

### Step 5: Install Project Dependencies

```bash
# Install all dependencies using Poetry
poetry install

# This will:
# - Create a virtual environment
# - Install all production and development dependencies
# - Install the project in development mode
```

### Step 6: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables if needed
nano .env  # or use your preferred editor

# Example .env content:
# TRADE_API_DEBUG=true
# TRADE_API_HOST=0.0.0.0
# TRADE_API_PORT=8000
# TRADE_API_MAX_TRADES_IN_MEMORY=10000
```

### Step 7: Verify Installation

```bash
# Run tests to verify everything works
poetry run pytest tests/test_setup.py -v

# Test application startup
poetry run python -c "from trade_api.main import app; print('✅ FastAPI app created successfully')"
```

### Step 8: Start the Application

#### Development Mode

```bash
# Start development server with auto-reload
poetry run uvicorn trade_api.main:app --host 0.0.0.0 --port 8000 --reload

# The API will be available at:
# - Local: http://localhost:8000
# - Network: http://<your-server-ip>:8000
# - API Docs: http://localhost:8000/docs
```

#### Production Mode

```bash
# Install production server (if not already installed)
poetry add gunicorn

# Start production server
poetry run gunicorn trade_api.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile -
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Poetry Not Found After Installation

```bash
# Manually add Poetry to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or install via pip as alternative
pip3 install poetry
```

#### 2. Python Version Compatibility Issues

```bash
# Check available Python versions
ls /usr/bin/python*

# If you have Python 3.11+ available, configure Poetry to use it
poetry env use python3.11

# Reinstall dependencies
poetry install
```

#### 3. Permission Issues

```bash
# If you get permission errors, ensure proper ownership
sudo chown -R $USER:$USER /path/to/project

# Or run with appropriate permissions
sudo -u $USER poetry install
```

#### 4. Network/Firewall Issues

```bash
# If running on a server, ensure port 8000 is open
sudo ufw allow 8000

# For cloud instances, check security groups/firewall rules
```

#### 5. Memory Issues on Small Systems

```bash
# If installation fails due to memory constraints, create swap
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make swap permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## System Service Setup (Optional)

### Create Systemd Service for Production

```bash
# Create service file
sudo nano /etc/systemd/system/trade-api.service
```

Add the following content:

```ini
[Unit]
Description=Trade API FastAPI Application
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/tcs-api
Environment=PATH=/home/www-data/.local/bin
ExecStart=/home/www-data/.local/bin/poetry run gunicorn trade_api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable trade-api
sudo systemctl start trade-api

# Check status
sudo systemctl status trade-api
```

## Docker Alternative (Recommended for Production)

### Create Dockerfile

```dockerfile
FROM python:3.11-slim-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml poetry.lock* ./
COPY src/ ./src/
COPY tests/ ./tests/

# Configure Poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# Expose port
EXPOSE 8000

# Start application
CMD ["poetry", "run", "gunicorn", "trade_api.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Build and Run Docker Container

```bash
# Build image
docker build -t trade-api .

# Run container
docker run -d -p 8000:8000 --name trade-api-container trade-api

# Check logs
docker logs trade-api-container
```

## Testing the Deployment

### Basic Health Check

```bash
# Test API endpoints
curl -X POST "http://localhost:8000/api/v1/trades/new" \
     -H "Content-Type: application/json" \
     -d '{"trade_type": "InterestRateSwap"}'

# Should return a JSON response with success: true
```

### Load Testing (Optional)

```bash
# Install Apache Bench for basic load testing
sudo apt install apache2-utils

# Test with 100 requests, 10 concurrent
ab -n 100 -c 10 -H "Content-Type: application/json" \
   -p post_data.json \
   http://localhost:8000/api/v1/trades/new
```

## Security Considerations

1. **Firewall**: Only open necessary ports
2. **User Permissions**: Run service as non-root user
3. **Environment Variables**: Keep sensitive data in environment files
4. **Updates**: Regularly update system packages and dependencies
5. **Monitoring**: Set up logging and monitoring for production use

## Performance Tuning

1. **Worker Processes**: Adjust based on CPU cores (typically 2x cores)
2. **Memory**: Monitor memory usage and adjust `max_trades_in_memory`
3. **Database**: Consider PostgreSQL for production persistence
4. **Caching**: Implement Redis for session/cache management
5. **Load Balancer**: Use nginx for multiple instances

## Monitoring and Logs

```bash
# View application logs
poetry run python -c "import logging; logging.basicConfig(level=logging.INFO)"

# System logs
sudo journalctl -u trade-api -f

# Performance monitoring
htop
iostat -x 1
```

This guide should get your Trade API running smoothly on any Debian-based system. Adjust paths and configurations based on your specific deployment requirements.