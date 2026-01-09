# TCS API - Trade Capture System API

A flexible, pipeline-based API system for processing financial swap deals with JSON-first architecture and modular design patterns.

## Overview

This API demonstrates enterprise-grade Python development using:
- **FastAPI** for high-performance async web services
- **Composition over Inheritance** design patterns
- **Modular Pipeline Architecture** for extensible business logic
- **JSON-first processing** with minimal object casting
- **Property-based testing** for comprehensive validation

## Supported Swap Types

- **Interest Rate Swaps (IRS)**: Fixed vs floating rate exchanges
- **Overnight Index Swaps (OIS)**: Fixed vs compounded overnight rates
- **Basis Swaps**: Two floating rate exchanges
- **Cross-Currency Swaps**: Multi-currency rate exchanges

## Quick Start

### Prerequisites
- Python 3.8+
- Poetry (recommended for dependency management)

### Installation

#### Option 1: Quick Setup Script (Recommended)
```bash
# Navigate to API directory
cd tcs-api

# Run the automated setup script
./setup.sh

# Start the development server
poetry run uvicorn trade_api.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Option 2: Docker (Easiest)
```bash
# Navigate to API directory
cd tcs-api

# Run the Docker setup script
./docker-setup.sh

# Choose your deployment option when prompted
```

#### Option 3: Manual Installation
```bash
# Install dependencies with Poetry
poetry install

# Copy environment configuration
cp .env.example .env

# Run the development server
poetry run uvicorn trade_api.main:app --reload
```

For detailed setup instructions on Debian/Ubuntu systems, see [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md).

## Deployment

### Files Included

- **`DEPLOYMENT_GUIDE.md`** - Comprehensive setup guide for Debian/Ubuntu systems
- **`setup.sh`** - Automated setup script for native installation
- **`docker-setup.sh`** - Automated Docker deployment script
- **`Dockerfile`** - Multi-stage Docker build configuration
- **`docker-compose.yml`** - Docker Compose configuration with optional nginx
- **`nginx.conf`** - Nginx reverse proxy configuration

### Quick Deployment Options

1. **Native Installation**: `./setup.sh`
2. **Docker Simple**: `./docker-setup.sh` (choose option 1)
3. **Docker with Compose**: `./docker-setup.sh` (choose option 2)
4. **Production with nginx**: `./docker-setup.sh` (choose option 3)

### API Endpoints

- `POST /new` - Create new trade templates
- `POST /save` - Save/update trade data
- `POST /validate` - Validate trade data

## Architecture

### Core Principles

1. **JSON Flexibility**: Work with trades as plain JSON, cast only when necessary
2. **Composition Pattern**: Use flexible schemas over rigid inheritance
3. **Pipeline Architecture**: Modular, pluggable operations for each endpoint

### Project Structure

```
tcs-api/
├── src/
│   └── trade_api/
│       ├── __init__.py
│       ├── main.py        # Application entry point and factory
│       ├── config.py      # Configuration management
│       ├── api/           # FastAPI endpoints and routes
│       ├── models/        # Data models and trade classes
│       ├── pipeline/      # Pipeline engine and stages
│       └── store/         # Trade persistence layer
├── tests/
│   ├── __init__.py
│   └── test_setup.py      # Basic setup verification tests
├── pyproject.toml         # Poetry configuration
├── .env.example          # Environment configuration template
└── README.md             # This file
```

## Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=trade_api

# Run property-based tests only
poetry run pytest tests/property/
```

### Development Server

```bash
# Development with auto-reload
poetry run uvicorn trade_api.main:app --reload

# Production-like setup
poetry run gunicorn trade_api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Enterprise Features

- **Modular Design**: Easy to extend with new trade types and operations
- **Comprehensive Testing**: Unit tests + property-based testing
- **Production Ready**: Gunicorn + Uvicorn deployment configuration
- **Type Safety**: Strategic use of Pydantic for API boundaries
- **Audit Trail**: Complete lifecycle tracking for all trades

## Documentation

- [Requirements](./.kiro/specs/trade-api/requirements.md)
- [Design Document](./.kiro/specs/trade-api/design.md)
- [Implementation Tasks](./.kiro/specs/trade-api/tasks.md)
- [Swap Analysis](../json-examples/swap-analysis.md)

## Contributing

This project serves as a template for enterprise Python API development. See the implementation tasks for development workflow.