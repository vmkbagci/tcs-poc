# Trade API

FastAPI-based Trade API system for processing financial swap deals.

## Overview

This API provides endpoints for creating, validating, and managing financial trade data including:
- Interest Rate Swaps (IR Swaps)
- Commodity Options
- Index Swaps

## Architecture

The system uses a layered architecture with:
- **API Layer**: FastAPI REST endpoints
- **Service Layer**: Business logic orchestration
- **Domain Model**: Trade data models with high-performance JSON operations
- **Validation Layer**: Plugin-based validation pipeline
- **Template Layer**: Component-based trade template system

## Quick Start

### Prerequisites

- Python 3.10+
- Poetry (Python dependency manager)

### Installation

```bash
# Run the setup script
./setup.sh

# Or manually:
poetry install
```

### Running the API

```bash
# Development server with auto-reload
poetry run uvicorn trade_api.main:app --host 0.0.0.0 --port 8000 --reload

# Production server
poetry run gunicorn trade_api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### API Endpoints

- `GET /api/v1/trades/new?trade_type={type}` - Create new trade from template
- `POST /api/v1/trades/validate` - Validate trade data
- `POST /api/v1/trades/save` - Save trade (placeholder)
- `GET /health` - Health check endpoint

### API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=trade_api

# Run property-based tests with more examples
HYPOTHESIS_PROFILE=thorough poetry run pytest tests/test_property_based.py

# Run specific test file
poetry run pytest tests/test_trade_service.py -v
```

## Project Structure

```
tcs-api/
├── src/trade_api/          # Source code
│   ├── api/                # API endpoints
│   ├── models/             # Domain models
│   ├── services/           # Business logic
│   └── validation/         # Validation pipeline
├── templates/              # Trade templates
│   └── v1/                 # Schema version 1
│       ├── core/           # Shared components
│       └── trade-types/    # Trade-specific templates
├── tests/                  # Test suite
│   ├── strategies/         # Hypothesis test generators
│   └── helpers/            # Test utilities
└── pyproject.toml          # Project dependencies
```

## Technology Stack

- **FastAPI**: Modern async web framework
- **Pydantic**: Data validation
- **orjson**: High-performance JSON
- **JMESPath**: JSON query language
- **glom**: Nested data operations
- **Hypothesis**: Property-based testing
- **pytest**: Testing framework

## Development

### Adding a New Trade Type

1. Create template files in `templates/v1/trade-types/{new-type}/`
2. Add validators in `src/trade_api/validation/validators/`
3. Register validators in `ValidationFactory`
4. Add tests in `tests/`

### Running Tests

```bash
# Quick tests (10 examples per property)
poetry run pytest

# Thorough tests (1000 examples per property)
HYPOTHESIS_PROFILE=thorough poetry run pytest

# Debug mode (verbose output)
HYPOTHESIS_PROFILE=debug poetry run pytest tests/test_property_based.py::test_date_ordering_invariant -v
```

## License

Copyright © 2026 Trade API Team
