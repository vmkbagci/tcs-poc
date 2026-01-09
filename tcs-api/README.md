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

```bash
# Navigate to API directory
cd tcs-api

# Install dependencies with Poetry
poetry install

# Activate virtual environment
poetry shell

# Run the development server
uvicorn src.trade_api.main:app --reload
```

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
│       ├── core/           # Core Trade class and interfaces
│       ├── pipeline/       # Pipeline engine and stages
│       ├── storage/        # Trade persistence layer
│       ├── api/           # FastAPI endpoints
│       └── main.py        # Application entry point
├── tests/
│   ├── unit/              # Unit tests
│   ├── property/          # Property-based tests
│   └── integration/       # Integration tests
├── pyproject.toml         # Poetry configuration
└── README.md             # This file
```

## Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/trade_api

# Run property-based tests only
poetry run pytest tests/property/
```

### Development Server

```bash
# Development with auto-reload
poetry run uvicorn src.trade_api.main:app --reload

# Production-like setup
poetry run gunicorn src.trade_api.main:app -w 4 -k uvicorn.workers.UvicornWorker
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