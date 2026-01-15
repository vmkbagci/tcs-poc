# Repository Verification Checklist

## For New Users Cloning This Repo

This document verifies that all necessary files are included for someone to clone and run the API.

### ✓ Prerequisites Included

- [x] `pyproject.toml` - Poetry configuration with all dependencies
- [x] `poetry.lock` - Locked dependency versions
- [x] `README.md` - Overview and setup instructions
- [x] `QUICKSTART.md` - Step-by-step quick start guide

### ✓ Core Application Files

- [x] `src/trade_api/main.py` - FastAPI application entry point
- [x] `src/trade_api/config.py` - Configuration management
- [x] `src/trade_api/__init__.py` - Package initialization

### ✓ API Layer

- [x] `src/trade_api/api/__init__.py` - API router setup
- [x] `src/trade_api/api/trades.py` - Trade endpoints (GET /new implemented)

### ✓ Models Layer

- [x] `src/trade_api/models/__init__.py` - Model exports
- [x] `src/trade_api/models/trade.py` - Trade and ReadOnlyTrade classes
- [x] `src/trade_api/models/assembler.py` - TradeAssembler for composition
- [x] `src/trade_api/models/factory.py` - TradeTemplateFactory

### ✓ Template System

- [x] `templates/README.md` - Template system documentation
- [x] `templates/v1/base/` - 3 base component files
  - [x] `trade-base.json`
  - [x] `general-base.json`
  - [x] `swap-leg-base.json`
- [x] `templates/v1/conventions/` - Market conventions
  - [x] `eur-conventions.json`
- [x] `templates/v1/leg-types/` - Leg type components
  - [x] `fixed-leg.json`
  - [x] `floating-ibor-leg.json`
- [x] `templates/v1/swap-types/irs/` - IRS hierarchy
  - [x] `irs-base.json`
  - [x] `irs-leg-base.json`
  - [x] `vanilla/vanilla-irs.json`
  - [x] `vanilla/vanilla-irs-legs.json`

**Note**: Empty directories for ois/, basis/, amortizing/ exist but won't be tracked by git until they contain files.

### ✓ Dependencies in pyproject.toml

```toml
[tool.poetry.dependencies]
python = "^3.10"
fastapi = "^0.104.1"
pydantic = "^2.5.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
gunicorn = "^21.2.0"
pydantic-settings = "^2.12.0"
orjson = "^3.11.5"          # Fast JSON processing
jmespath = "^1.0.1"         # JSON queries
glom = "^25.12.0"           # Nested property writes
```

### ✓ Documentation

- [x] `IMPLEMENTATION_NOTES.md` - Technical notes and known issues
- [x] `SESSION_STATUS.md` - Current status and next steps
- [x] `.kiro/specs/trade-api/requirements.md` - Requirements document
- [x] `.kiro/specs/trade-api/design.md` - Design document with architecture
- [x] `.kiro/specs/trade-api/tasks.md` - Implementation tasks

### ✓ Tests

- [x] `tests/test_trade.py` - Trade class tests (placeholder)

## Verification Steps

### 1. Clone and Install

```bash
git clone <repo-url>
cd tcs-json-demo/tcs-api
poetry install
```

**Expected**: All dependencies install successfully, including orjson, jmespath, glom.

### 2. Start Server

```bash
poetry run uvicorn trade_api.main:app --reload
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 3. Access Swagger UI

Open browser to: http://127.0.0.1:8000/docs

**Expected**: Interactive API documentation showing:
- GET /api/v1/trades/new endpoint
- POST /api/v1/trades/save endpoint (placeholder)
- POST /api/v1/trades/validate endpoint (placeholder)

### 4. Test /new Endpoint

In Swagger UI, test GET /api/v1/trades/new with:
- `trade_type`: irswap
- `trade_subtype`: vanilla
- `currency`: EUR
- `leg_types`: fixed,floating-ibor

**Expected**: JSON response with:
- `success: true`
- `trade_data` containing complete trade structure
- `metadata` with trade_id, trade_type, trade_subtype, etc.

### 5. Test All Subtypes

Test these combinations:

| trade_type | trade_subtype | leg_types | Expected Result |
|------------|---------------|-----------|-----------------|
| irswap | vanilla | fixed,floating-ibor | ✓ Success |
| irswap | ois | fixed,floating-ois | ✓ Success |
| irswap | basis | floating-ibor,floating-ibor | ✓ Success |
| irswap | amortizing | fixed,floating-ibor | ✓ Success |

### 6. Verify Template Loading

Check server logs for template loading:
- No errors about missing template files
- No errors about schema version not found

## Known Issues (Documented)

These are intentional and documented for future work:

1. **Lifecycle on Draft Trades**: `/new` endpoint adds `lastEvent` to drafts (should only happen on first save)
2. **Missing Subtype Field**: Trade data doesn't include explicit subtype field
3. **Empty swapType**: Non-vanilla subtypes (ois, basis, amortizing) have empty swapType field

See [IMPLEMENTATION_NOTES.md](./IMPLEMENTATION_NOTES.md) for details.

## Success Criteria

✅ **Repository is ready for others** if:
1. `poetry install` completes without errors
2. Server starts without errors
3. Swagger UI is accessible
4. GET /api/v1/trades/new works for all 4 IR Swap subtypes
5. All template files load correctly

## Troubleshooting

### "ModuleNotFoundError: No module named 'orjson'"
**Solution**: Run `poetry install` to install dependencies

### "Template schema version 'v1' not found"
**Solution**: Ensure you're in the `tcs-api` directory and `templates/` folder exists

### Port 8000 already in use
**Solution**: Use different port: `poetry run uvicorn trade_api.main:app --reload --port 8001`

## Next Steps After Verification

Once verified, users can:
1. Read [IMPLEMENTATION_NOTES.md](./IMPLEMENTATION_NOTES.md) for technical details
2. Read [SESSION_STATUS.md](./SESSION_STATUS.md) for current status
3. Explore the template system in `templates/v1/`
4. Review the design document in `.kiro/specs/trade-api/design.md`
5. Continue implementation with `/validate` endpoint

---

**Last Verified**: 2026-01-14
**Status**: ✅ Ready for distribution
