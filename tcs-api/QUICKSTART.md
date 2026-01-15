# Quick Start Guide

## Setup and Run (5 minutes)

### 1. Install Dependencies

```bash
cd tcs-api
poetry install
```

This will install:
- FastAPI (web framework)
- orjson (fast JSON processing)
- jmespath (JSON queries)
- glom (nested property writes)
- uvicorn (ASGI server)
- All other dependencies

### 2. Start the Server

```bash
poetry run uvicorn trade_api.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 3. Test the API

#### Option A: Use Swagger UI (Easiest)

Open your browser to: **http://127.0.0.1:8000/docs**

You'll see the interactive API documentation. Try the `/api/v1/trades/new` endpoint:
1. Click on "GET /api/v1/trades/new"
2. Click "Try it out"
3. Fill in parameters:
   - `trade_type`: irswap
   - `trade_subtype`: vanilla
   - `currency`: EUR
   - `leg_types`: fixed,floating-ibor
4. Click "Execute"

#### Option B: Use curl

```bash
# Create a vanilla EUR IRS
curl "http://127.0.0.1:8000/api/v1/trades/new?trade_type=irswap&trade_subtype=vanilla&currency=EUR&leg_types=fixed,floating-ibor" | python3 -m json.tool

# Create an OIS
curl "http://127.0.0.1:8000/api/v1/trades/new?trade_type=irswap&trade_subtype=ois&currency=EUR&leg_types=fixed,floating-ois" | python3 -m json.tool

# Create a basis swap
curl "http://127.0.0.1:8000/api/v1/trades/new?trade_type=irswap&trade_subtype=basis&currency=EUR&leg_types=floating-ibor,floating-ibor" | python3 -m json.tool

# Create an amortizing swap
curl "http://127.0.0.1:8000/api/v1/trades/new?trade_type=irswap&trade_subtype=amortizing&currency=EUR&leg_types=fixed,floating-ibor" | python3 -m json.tool
```

### 4. Verify It Works

You should get a JSON response like:

```json
{
  "success": true,
  "trade_data": {
    "tradeId": "SWAP-20260114-IRSWAP-VANILLA-1234",
    "tradeType": "InterestRateSwap",
    "version": 1,
    "status": "Confirmed",
    "general": { ... },
    "swapDetails": {
      "swapType": "vanillaFixedFloat",
      "currency": "EUR",
      "conventions": { ... }
    },
    "legs": [
      {
        "legType": "Pay",
        "rateType": "fixed",
        ...
      },
      {
        "legType": "Receive",
        "rateType": "floating",
        ...
      }
    ],
    "lastEvent": { ... }
  },
  "errors": [],
  "warnings": [],
  "metadata": {
    "trade_id": "SWAP-20260114-IRSWAP-VANILLA-1234",
    "trade_type": "irswap",
    "trade_subtype": "vanilla",
    "currency": "EUR",
    "leg_count": 2,
    "template_schema_version": "v1"
  }
}
```

## Available Endpoints

### GET /api/v1/trades/new ✓ (Implemented)

Create a new trade template.

**Parameters**:
- `trade_type` (required): "irswap" or "xccy"
- `trade_subtype` (required): "vanilla", "ois", "basis", "amortizing"
- `currency` (optional, default "EUR"): Currency code
- `leg_types` (optional, default "fixed,floating-ibor"): Comma-separated leg types

**Supported Combinations**:
- **Vanilla IRS**: `trade_type=irswap&trade_subtype=vanilla&leg_types=fixed,floating-ibor`
- **OIS**: `trade_type=irswap&trade_subtype=ois&leg_types=fixed,floating-ois`
- **Basis Swap**: `trade_type=irswap&trade_subtype=basis&leg_types=floating-ibor,floating-ibor`
- **Amortizing IRS**: `trade_type=irswap&trade_subtype=amortizing&leg_types=fixed,floating-ibor`

### POST /api/v1/trades/save (Placeholder)

Save or update a trade. Not yet implemented.

### POST /api/v1/trades/validate (Placeholder)

Validate trade data. Not yet implemented.

## Troubleshooting

### "ModuleNotFoundError: No module named 'orjson'"

Run: `poetry install`

### "Template schema version 'v1' not found"

Make sure you're running from the `tcs-api` directory and the `templates/` folder exists.

### Server won't start

Check if port 8000 is already in use:
```bash
lsof -i :8000
```

Use a different port:
```bash
poetry run uvicorn trade_api.main:app --reload --port 8001
```

## Next Steps

- Read [IMPLEMENTATION_NOTES.md](./IMPLEMENTATION_NOTES.md) for technical details
- Read [SESSION_STATUS.md](./SESSION_STATUS.md) for current status and known issues
- Check [.kiro/specs/trade-api/design.md](./.kiro/specs/trade-api/design.md) for architecture
- Explore the template system in `templates/v1/`

## Architecture Highlights

### Hierarchical Template System

Templates are organized in a hierarchy:
```
base → type → subtype → market → leg-specific
```

Example for Vanilla EUR IRS:
1. `base/trade-base.json` - Universal fields
2. `swap-types/irs/irs-base.json` - All IRS swaps
3. `swap-types/irs/vanilla/vanilla-irs.json` - Vanilla specific
4. `conventions/eur-conventions.json` - EUR market rules
5. `leg-types/fixed-leg.json` + `leg-types/floating-ibor-leg.json` - Leg specifics

### Trade Class

Uses high-performance libraries:
- **orjson**: 2-3x faster JSON parsing than stdlib
- **jmespath**: Powerful JSON queries (filters, projections)
- **glom**: Robust nested property writes

```python
from trade_api.models import Trade

trade = Trade(trade_dict)
currency = trade.jmesget("swapDetails.currency")  # JMESPath query
trade.glomset("legs.0.notional", 1000000)  # Nested write
```

## Known Issues

See [IMPLEMENTATION_NOTES.md](./IMPLEMENTATION_NOTES.md) for:
- Lifecycle/lastEvent on draft trades (to be fixed)
- Missing subtype field in trade data (to be fixed)
- Empty swapType for non-vanilla subtypes (to be fixed)
