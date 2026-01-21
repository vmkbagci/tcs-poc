# TCS Store API Examples

This directory contains example scripts, trade payloads, and context metadata to help you get started with the TCS Store API.

## Files

- **example_client.py**: Complete Python client demonstrating all API operations
- **example_trades.json**: Sample trade payloads for different trade types
- **example_contexts.json**: Sample context metadata for various scenarios

## Running the Example Client

### Prerequisites

1. Start the TCS Store API:
   ```bash
   cd tcs-store
   ./run-store.sh
   ```

2. Ensure the API is running at http://localhost:5500

### Run the Examples

```bash
poetry run python examples/example_client.py
```

The script will demonstrate:
- Saving new trades with context metadata
- Loading trades by ID
- Full updates (complete replacement)
- Partial updates (deep merge)
- Null handling in partial updates
- Filtering trades (equality, range, regex, multiple conditions)
- Listing and counting trades
- Bulk load operations
- Deleting trades (single and bulk)
- Idempotent delete behavior

## Example Trade Payloads

The `example_trades.json` file contains sample trades for:

1. **Simple IR Swap**: Basic interest rate swap
2. **IR Swap with Legs**: Swap with detailed leg information
3. **IR Swap with Schedule**: Swap with payment schedules
4. **FX Swap**: Foreign exchange swap with near and far legs
5. **Commodity Option**: Commodity option trade
6. **Trade with Metadata**: Trade with tags and notes
7. **Minimal Trade**: Minimal required fields
8. **Complex Nested Trade**: Deeply nested trade structure with pricing and risk metrics

### Using Example Trades

```python
import json
import requests

# Load example trades
with open('examples/example_trades.json', 'r') as f:
    data = json.load(f)

# Get a specific trade
ir_swap = data['trades'][0]['trade']

# Save to API
payload = {
    "context": {
        "user": "trader_john",
        "agent": "example_script",
        "action": "save_new",
        "intent": "testing"
    },
    "trade": ir_swap
}

response = requests.post('http://localhost:5500/save/new', json=payload)
print(response.json())
```

## Example Context Metadata

The `example_contexts.json` file contains context metadata for various scenarios:

### Manual Trading Operations
- New trade booking (manual entry)
- Trade corrections (counterparty, notional, schedule)
- Trade cancellations

### Automated System Operations
- Automated trading execution
- Price updates from reconciliation
- Risk metrics refresh
- End of day processing
- Matured trade cleanup

### Bulk Operations
- Initial data migration
- Daily reconciliation imports
- Portfolio cleanup
- Test data cleanup

### Specialized Operations
- Regulatory reporting updates
- Collateral management updates
- Legal terms amendments
- Confirmation status updates

### Using Example Contexts

```python
import json
import requests

# Load example contexts
with open('examples/example_contexts.json', 'r') as f:
    data = json.load(f)

# Get a specific context
new_trade_context = data['contexts'][0]['context']

# Use in API request
payload = {
    "context": new_trade_context,
    "trade": {
        "id": "my_trade_id",
        "data": {"trade_type": "IR_SWAP", "notional": 1000000}
    }
}

response = requests.post('http://localhost:5500/save/new', json=payload)
```

## Context Metadata Guidelines

### Required Fields

All mutating operations (save, delete) require context metadata with these fields:

- **user**: Identifier of the person or service account
  - Examples: `"trader_john_smith"`, `"system_reconciliation"`
  
- **agent**: Identifier of the application or service
  - Examples: `"trading_ui"`, `"reconciliation_service"`
  
- **action**: The operation being performed
  - Examples: `"save_new"`, `"update"`, `"partial_update"`, `"delete"`, `"bulk_delete"`
  
- **intent**: The business reason or workflow step
  - Examples: `"new_trade_booking"`, `"counterparty_correction"`, `"automated_price_update"`

### When Context is Required

**Required for:**
- All save operations (`/save/new`, `/save/update`, `/save/partial`)
- All delete operations (`/delete/id`, `/delete/group`)

**NOT required for:**
- All load operations (`/load/id`, `/load/group`, `/load/filter`)
- All list operations (`/list`, `/list/count`)
- Health check (`/health`)

## Filter Examples

### Equality Filter

```python
payload = {
    "filter": {
        "data.trade_type": {"eq": "IR_SWAP"}
    }
}
```

### Range Filter

```python
payload = {
    "filter": {
        "data.notional": {
            "gte": 1000000,
            "lte": 10000000
        }
    }
}
```

### Regex Filter

```python
payload = {
    "filter": {
        "data.counterparty": {"regex": "^BANK.*"}
    }
}
```

### Multiple Conditions (AND Logic)

```python
payload = {
    "filter": {
        "data.trade_type": {"eq": "IR_SWAP"},
        "data.notional": {"gte": 1000000},
        "data.currency": {"eq": "USD"}
    }
}
```

### Nested Field Paths

```python
payload = {
    "filter": {
        "data.leg1.schedule.start_date": {"gte": "2024-01-01"},
        "data.leg1.notional": {"gt": 500000}
    }
}
```

## Deep Merge Examples

### Basic Field Update

```python
# Existing trade
{
    "id": "trade_123",
    "data": {
        "trade_type": "IR_SWAP",
        "notional": 1000000,
        "counterparty": "BANK_A"
    }
}

# Partial update
{
    "context": {...},
    "id": "trade_123",
    "updates": {
        "data": {
            "notional": 1500000  # Only update notional
        }
    }
}

# Result: notional updated, other fields preserved
```

### Nested Object Merge

```python
# Existing trade
{
    "id": "trade_123",
    "data": {
        "leg1": {
            "notional": 1000000,
            "rate": 0.045
        }
    }
}

# Partial update
{
    "context": {...},
    "id": "trade_123",
    "updates": {
        "data": {
            "leg1": {
                "rate": 0.048  # Only update rate
            }
        }
    }
}

# Result: leg1.rate updated, leg1.notional preserved
```

### Null Handling - Remove Object

```python
# Partial update
{
    "context": {...},
    "id": "trade_123",
    "updates": {
        "data": {
            "metadata": null  # Remove entire metadata object
        }
    }
}
```

### Null Handling - Set Primitive to Null

```python
# Partial update
{
    "context": {...},
    "id": "trade_123",
    "updates": {
        "data": {
            "broker": null  # Set broker field to null
        }
    }
}
```

## Additional Resources

- **API Documentation**: http://localhost:5500/docs
- **OpenAPI Schema**: http://localhost:5500/openapi.json
- **Main README**: ../README.md

## Support

For questions or issues, please refer to the main README or API documentation.
