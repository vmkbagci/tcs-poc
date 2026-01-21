# TCS Store

In-memory trade storage API with lifecycle tracing.

## Overview

The TCS Store API provides RESTful endpoints for managing trade data in memory with comprehensive lifecycle tracing through context metadata. It runs on **port 5500** by default to enable full integration testing alongside other services:

- **UI**: Port 4200
- **Business API (tcs-api)**: Port 5000
- **Store API (tcs-store)**: Port 5500

## Table of Contents

- [Setup](#setup)
- [Running the Service](#running-the-service)
- [Testing](#testing)
- [API Endpoints](#api-endpoints)
- [Context Metadata](#context-metadata)
- [Filter Syntax](#filter-syntax)
- [Deep Merge Behavior](#deep-merge-behavior)
- [Architecture](#architecture)
- [Development](#development)

## Setup

### Prerequisites

- Python 3.11 or higher
- Poetry (Python package manager)

### Installation

Install dependencies using Poetry:

```bash
poetry install
```

## Running the Service

### Quick Start (Development Mode)

Using the startup script (recommended):

```bash
./run-store.sh
```

Or manually with Poetry:

```bash
poetry run uvicorn tcs_store.main:app --host 0.0.0.0 --port 5500 --reload
```

### Available Modes

```bash
./run-store.sh dev      # Development mode with auto-reload (default)
./run-store.sh prod     # Production mode with Gunicorn workers
./run-store.sh test     # Run tests before starting server
./run-store.sh help     # Show help message
```

### Environment Variables

You can customize the server configuration using environment variables:

```bash
export TCS_STORE_HOST=0.0.0.0      # Host to bind to (default: 0.0.0.0)
export TCS_STORE_PORT=5500         # Port to bind to (default: 5500)
export TCS_STORE_WORKERS=4         # Number of workers for production (default: 4)
```

### Access the API

Once running, the API will be available at:

- **API Base**: http://localhost:5500
- **API Documentation**: http://localhost:5500/docs
- **OpenAPI Schema**: http://localhost:5500/openapi.json

## Testing

### Run All Tests

```bash
poetry run pytest
```

### Run Specific Test Suites

```bash
poetry run pytest tests/unit/              # Unit tests only
poetry run pytest tests/property/          # Property-based tests only
poetry run pytest tests/integration/       # Integration tests only
```

### Run with Coverage

```bash
poetry run pytest --cov=tcs_store --cov-report=html
```

View coverage report:

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## API Endpoints

All endpoints use POST method for consistency and to support complex request bodies.

### Save Operations

#### POST /save/new

Save a new trade to the store.

**Request:**
```json
{
  "context": {
    "user": "trader_123",
    "agent": "trading_platform",
    "action": "save_new",
    "intent": "new_trade_booking"
  },
  "trade": {
    "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
    "data": {
      "trade_type": "IR_SWAP",
      "counterparty": "BANK_A",
      "notional": 1000000,
      "trade_date": "2024-01-15"
    }
  }
}
```

**Response (201 Created):**
```json
{
  "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "data": {
    "trade_type": "IR_SWAP",
    "counterparty": "BANK_A",
    "notional": 1000000,
    "trade_date": "2024-01-15"
  }
}
```

**Error Response (409 Conflict):**
```json
{
  "error": "Trade already exists",
  "detail": "Trade with ID a1b2c3d4... already exists"
}
```

#### POST /save/update

Update an existing trade (full replacement).

**Request:**
```json
{
  "context": {
    "user": "trader_123",
    "agent": "trading_platform",
    "action": "update",
    "intent": "trade_correction"
  },
  "trade": {
    "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
    "data": {
      "trade_type": "IR_SWAP",
      "counterparty": "BANK_B",
      "notional": 2000000,
      "trade_date": "2024-01-15"
    }
  }
}
```

**Response (200 OK):**
```json
{
  "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "data": {
    "trade_type": "IR_SWAP",
    "counterparty": "BANK_B",
    "notional": 2000000,
    "trade_date": "2024-01-15"
  }
}
```

#### POST /save/partial

Partially update a trade using deep merge.

**Request:**
```json
{
  "context": {
    "user": "trader_123",
    "agent": "trading_platform",
    "action": "partial_update",
    "intent": "notional_adjustment"
  },
  "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "updates": {
    "data": {
      "notional": 1500000
    }
  }
}
```

**Response (200 OK):**
```json
{
  "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "data": {
    "trade_type": "IR_SWAP",
    "counterparty": "BANK_A",
    "notional": 1500000,
    "trade_date": "2024-01-15"
  }
}
```

### Load Operations

#### POST /load/id

Load a single trade by ID.

**Request:**
```json
{
  "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
}
```

**Response (200 OK):**
```json
{
  "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "data": {
    "trade_type": "IR_SWAP",
    "counterparty": "BANK_A",
    "notional": 1000000,
    "trade_date": "2024-01-15"
  }
}
```

**Error Response (404 Not Found):**
```json
{
  "error": "Trade not found",
  "detail": "Trade with ID a1b2c3d4... not found"
}
```

#### POST /load/group

Load multiple trades by IDs.

**Request:**
```json
{
  "ids": [
    "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
    "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6a7",
    "c3d4e5f6g7h8i9j0k1l2m3n4o5p6a7b8"
  ]
}
```

**Response (200 OK):**
```json
{
  "trades": [
    {
      "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
      "data": {...}
    },
    {
      "id": "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6a7",
      "data": {...}
    }
  ],
  "missing_ids": ["c3d4e5f6g7h8i9j0k1l2m3n4o5p6a7b8"]
}
```

#### POST /load/filter

Load trades matching filter criteria.

**Request:**
```json
{
  "filter": {
    "data.trade_type": {"eq": "IR_SWAP"},
    "data.notional": {"gte": 1000000}
  }
}
```

**Response (200 OK):**
```json
{
  "trades": [
    {
      "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
      "data": {...}
    }
  ]
}
```

### List Operations

#### POST /list

List trades matching filter criteria (returns simplified list items).

**Request:**
```json
{
  "filter": {
    "data.trade_type": {"eq": "IR_SWAP"}
  }
}
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
      "data": {...}
    }
  ]
}
```

#### POST /list/count

Count trades matching filter criteria.

**Request:**
```json
{
  "filter": {
    "data.trade_type": {"eq": "IR_SWAP"}
  }
}
```

**Response (200 OK):**
```json
{
  "count": 42
}
```

### Delete Operations

#### POST /delete/id

Delete a single trade by ID.

**Request:**
```json
{
  "context": {
    "user": "trader_123",
    "agent": "trading_platform",
    "action": "delete",
    "intent": "trade_cancellation"
  },
  "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
}
```

**Response (200 OK):**
```json
{
  "message": "Trade deleted successfully"
}
```

**Note:** Delete operations are idempotent. Deleting a non-existent trade returns 200 OK.

#### POST /delete/group

Delete multiple trades by IDs.

**Request:**
```json
{
  "context": {
    "user": "trader_123",
    "agent": "trading_platform",
    "action": "bulk_delete",
    "intent": "portfolio_cleanup"
  },
  "ids": [
    "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
    "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6a7"
  ]
}
```

**Response (200 OK):**
```json
{
  "deleted_count": 2,
  "missing_ids": []
}
```

### Admin Operations (Testing/Development Only)

**⚠️ WARNING: These endpoints are for testing and development only. DO NOT USE IN PRODUCTION.**

#### POST /admin/purge

Purge/clear all trades from the store (DANGEROUS).

**Request:**
```json
{
  "context": {
    "user": "admin_user",
    "agent": "admin_ui",
    "action": "purge",
    "intent": "test_cleanup"
  }
}
```

**Response (200 OK):**
```json
{
  "message": "Store purged successfully",
  "trades_deleted": 42
}
```

**Use Cases:**
- Cleaning up after integration tests
- Resetting QA environments
- Development environment cleanup

#### POST /admin/seed

Seed the store with randomly generated IR swap trades.

**Request:**
```json
{
  "context": {
    "user": "admin_user",
    "agent": "admin_ui",
    "action": "seed",
    "intent": "test_data_setup"
  },
  "count": 10
}
```

**Response (201 Created):**
```json
{
  "message": "Successfully seeded 10 IR swap trades",
  "trades_created": 10,
  "trade_ids": [
    "IR_SWAP_A1B2C3D4E5F6G7H8",
    "IR_SWAP_B2C3D4E5F6G7H8I9"
  ]
}
```

**Generated Trade Variations:**
- Random notionals: 1,000 to 100,000
- Random fixed rates: 2.5% to 5.0%
- Random margins: -0.5% to 0.5%
- Random durations: 1 to 36 months
- Random counterparties, books, and traders
- Unique trade IDs

**Use Cases:**
- Setting up test data for UI development
- Preparing demo environments
- Integration testing with realistic data
- Performance testing

### Health Check

#### GET /health

Check service health (no context required).

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

## Context Metadata

### Overview

Context metadata enables lifecycle tracing and audit trails for all mutating operations. Every save and delete operation **must** include context metadata.

### Required Fields

- **user**: Identifier of the person or service account making the request (e.g., "trader_123", "system_reconciliation")
- **agent**: Identifier of the application or service making the request (e.g., "trading_platform", "risk_engine")
- **action**: The operation being performed (e.g., "save_new", "update", "delete", "bulk_delete")
- **intent**: The business reason or workflow step (e.g., "new_trade_booking", "trade_correction", "portfolio_cleanup")

### When Context is Required

**Required for:**
- All save operations (`/save/new`, `/save/update`, `/save/partial`)
- All delete operations (`/delete/id`, `/delete/group`)

**Not required for:**
- All load operations (`/load/id`, `/load/group`, `/load/filter`)
- All list operations (`/list`, `/list/count`)
- Health check (`/health`)

### Context Examples

**New Trade Booking:**
```json
{
  "user": "trader_john",
  "agent": "trading_ui",
  "action": "save_new",
  "intent": "new_trade_booking"
}
```

**Trade Correction:**
```json
{
  "user": "trader_jane",
  "agent": "trading_ui",
  "action": "update",
  "intent": "counterparty_correction"
}
```

**Automated Reconciliation:**
```json
{
  "user": "system_reconciliation",
  "agent": "reconciliation_service",
  "action": "partial_update",
  "intent": "automated_price_update"
}
```

**Trade Cancellation:**
```json
{
  "user": "trader_john",
  "agent": "trading_ui",
  "action": "delete",
  "intent": "trade_cancellation"
}
```

### Validation Errors

If context is missing or incomplete, the API returns 422 Unprocessable Entity:

```json
{
  "error": "Invalid context",
  "detail": "Context field 'user' is required"
}
```

## Filter Syntax

### Overview

Filters enable querying trades based on field values using various operators. Filters support nested field paths and multiple conditions with AND logic.

### Supported Operators

- **eq**: Equals
- **ne**: Not equals
- **gt**: Greater than
- **gte**: Greater than or equal to
- **lt**: Less than
- **lte**: Less than or equal to
- **regex**: Regular expression matching (Python `re` module)
- **in**: Value in list
- **nin**: Value not in list

### Filter Structure

```json
{
  "filter": {
    "field.path": {"operator": "value"}
  }
}
```

### Examples

#### Simple Equality

```json
{
  "filter": {
    "data.trade_type": {"eq": "IR_SWAP"}
  }
}
```

#### Range Query

```json
{
  "filter": {
    "data.notional": {
      "gte": 1000000,
      "lte": 10000000
    }
  }
}
```

#### Regular Expression

```json
{
  "filter": {
    "data.counterparty": {"regex": "^BANK.*"}
  }
}
```

#### List Membership

```json
{
  "filter": {
    "data.trade_type": {"in": ["IR_SWAP", "FX_SWAP", "COMMODITY_OPTION"]}
  }
}
```

#### Multiple Conditions (AND Logic)

```json
{
  "filter": {
    "data.trade_type": {"eq": "IR_SWAP"},
    "data.notional": {"gte": 1000000},
    "data.counterparty": {"regex": "^BANK.*"},
    "data.trade_date": {"gte": "2024-01-01"}
  }
}
```

#### Nested Field Paths

```json
{
  "filter": {
    "data.leg1.schedule.start_date": {"gte": "2024-01-01"},
    "data.leg1.notional": {"gt": 500000}
  }
}
```

#### Empty Filter (Returns All Trades)

```json
{
  "filter": {}
}
```

### Filter Behavior

- **AND Logic**: Multiple conditions are combined with AND logic (all must match)
- **Nested Paths**: Use dot notation to access nested fields (e.g., `data.leg1.notional`)
- **Missing Fields**: Trades without the specified field do not match the filter
- **Type Matching**: Operators respect field types (numeric comparisons for numbers, string comparisons for strings)

## Deep Merge Behavior

### Overview

The `/save/partial` endpoint uses deep merge to update trades. This allows updating specific nested fields without replacing the entire trade object.

### Merge Rules

1. **Nested Dictionaries**: Merged recursively
2. **Lists**: Replaced entirely (not merged)
3. **Primitives**: Replaced with new value
4. **Null Handling**: Smart behavior based on existing value type

### Null Handling

The deep merge implements smart null handling:

- **Object/Dict + null**: Field is **removed**
- **Primitive + null**: Field is **set to null**

### Examples

#### Basic Field Update

**Existing Trade:**
```json
{
  "id": "abc123",
  "data": {
    "trade_type": "IR_SWAP",
    "counterparty": "BANK_A",
    "notional": 1000000
  }
}
```

**Partial Update:**
```json
{
  "data": {
    "notional": 1500000
  }
}
```

**Result:**
```json
{
  "id": "abc123",
  "data": {
    "trade_type": "IR_SWAP",
    "counterparty": "BANK_A",
    "notional": 1500000
  }
}
```

#### Nested Object Merge

**Existing Trade:**
```json
{
  "id": "abc123",
  "data": {
    "leg1": {
      "notional": 1000000,
      "currency": "USD"
    },
    "leg2": {
      "notional": 1000000,
      "currency": "EUR"
    }
  }
}
```

**Partial Update:**
```json
{
  "data": {
    "leg1": {
      "notional": 1500000
    }
  }
}
```

**Result:**
```json
{
  "id": "abc123",
  "data": {
    "leg1": {
      "notional": 1500000,
      "currency": "USD"
    },
    "leg2": {
      "notional": 1000000,
      "currency": "EUR"
    }
  }
}
```

#### Null Handling - Remove Object

**Existing Trade:**
```json
{
  "id": "abc123",
  "data": {
    "leg1": {"notional": 1000000},
    "leg2": {"notional": 1000000}
  }
}
```

**Partial Update:**
```json
{
  "data": {
    "leg2": null
  }
}
```

**Result:**
```json
{
  "id": "abc123",
  "data": {
    "leg1": {"notional": 1000000}
  }
}
```

#### Null Handling - Set Primitive to Null

**Existing Trade:**
```json
{
  "id": "abc123",
  "data": {
    "counterparty": "BANK_A",
    "broker": "BROKER_X"
  }
}
```

**Partial Update:**
```json
{
  "data": {
    "broker": null
  }
}
```

**Result:**
```json
{
  "id": "abc123",
  "data": {
    "counterparty": "BANK_A",
    "broker": null
  }
}
```

#### List Replacement

**Existing Trade:**
```json
{
  "id": "abc123",
  "data": {
    "tags": ["urgent", "high-value"]
  }
}
```

**Partial Update:**
```json
{
  "data": {
    "tags": ["reviewed", "approved"]
  }
}
```

**Result:**
```json
{
  "id": "abc123",
  "data": {
    "tags": ["reviewed", "approved"]
  }
}
```

## Architecture

The application follows a three-layer architecture:

### Layers

1. **API Layer** (`api/`): FastAPI route handlers that define endpoints and handle HTTP concerns
2. **Service Layer** (`services/`): Business logic for trade operations, validation, and filtering
3. **Storage Layer** (`storage/`): In-memory data store with thread-safe access

### Architecture Diagram

```
┌─────────────────────────────────────┐
│         FastAPI Application         │
├─────────────────────────────────────┤
│          API Routes Layer           │
│  /save, /load, /list, /delete       │
├─────────────────────────────────────┤
│         Service Layer               │
│  TradeService (business logic)      │
├─────────────────────────────────────┤
│         Storage Layer               │
│  InMemoryStore (thread-safe dict)   │
└─────────────────────────────────────┘
```

### Key Components

- **InMemoryStore**: Thread-safe dictionary storage with operation logging
- **TradeService**: Business logic, validation, filtering, and deep merge
- **API Routes**: FastAPI endpoints with request/response handling
- **Pydantic Models**: Request/response validation and serialization

### Thread Safety

All storage operations use `threading.RLock` for thread-safe concurrent access.

### Lifecycle Tracing

Context metadata is logged for all mutating operations with timestamps for audit trails.

## Development

### Project Structure

```
tcs-store/
├── src/tcs_store/
│   ├── api/                    # API endpoints
│   │   ├── save.py            # Save operations
│   │   ├── load.py            # Load operations
│   │   ├── list.py            # List operations
│   │   ├── delete.py          # Delete operations
│   │   └── health.py          # Health check
│   ├── models/                 # Pydantic models
│   │   ├── context.py         # Context metadata
│   │   ├── filter.py          # Filter models
│   │   ├── requests.py        # Request models
│   │   └── responses.py       # Response models
│   ├── services/               # Business logic
│   │   └── trade_service.py   # Trade service
│   ├── storage/                # Storage layer
│   │   └── in_memory_store.py # In-memory storage
│   ├── exceptions.py           # Custom exceptions
│   └── main.py                 # FastAPI application
├── tests/
│   ├── unit/                   # Unit tests
│   ├── property/               # Property-based tests
│   └── integration/            # Integration tests
├── pyproject.toml              # Poetry configuration
├── run-store.sh                # Startup script
└── README.md                   # This file
```

### Running Multiple Services

To run all services for full integration testing:

```bash
# Terminal 1 - UI
cd tcs-ui
npm start                    # Runs on port 4200

# Terminal 2 - Business API
cd tcs-api
./run-api.sh                 # Runs on port 5000

# Terminal 3 - Store API
cd tcs-store
./run-store.sh               # Runs on port 5500
```

### Code Style

The project follows Python best practices:

- PEP 8 style guide
- Type hints for all functions
- Docstrings for all public APIs
- Comprehensive test coverage (90%+ line coverage)

### Contributing

1. Write tests for new features
2. Ensure all tests pass: `poetry run pytest`
3. Check code coverage: `poetry run pytest --cov=tcs_store`
4. Follow existing code style and patterns

## License

Proprietary - Internal use only
