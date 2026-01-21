# Running All TCS Services

Quick reference for starting all three TCS services for development and testing.

---

## Service Ports

- **tcs-store**: Port 5500 (Storage API)
- **tcs-api**: Port 5000 (Business Logic API)
- **tcs-ui**: Port 4200 (Angular UI)

---

## Starting Services

### Option 1: Start All Services Manually

Open three terminal windows:

**Terminal 1 - TCS Store:**
```bash
cd tcs-store
./run-store.sh
```

**Terminal 2 - TCS API:**
```bash
cd tcs-api
./run-api.sh
```

**Terminal 3 - TCS UI:**
```bash
cd tcs-ui
npm start
# or
ng serve
```

### Option 2: Run Integration Tests (Auto-starts API + Store)

```bash
./run-integration-tests.sh
```

This script will:
1. Check if tcs-store and tcs-api are running
2. Start them if needed
3. Run integration tests
4. Clean up services it started

---

## Health Checks

Verify services are running:

```bash
# Check tcs-store
curl http://localhost:5500/health

# Check tcs-api
curl http://localhost:5000/health

# Check tcs-ui (in browser)
open http://localhost:4200
```

---

## Stopping Services

Press `Ctrl+C` in each terminal window, or:

```bash
# Kill all services
pkill -f "uvicorn.*tcs_store"
pkill -f "uvicorn.*trade_api"
pkill -f "ng serve"
```

---

## Service Dependencies

```
tcs-ui (4200)
    ↓
tcs-api (5000)
    ↓
tcs-store (5500)
```

- **tcs-ui** calls **tcs-api** endpoints
- **tcs-api** calls **tcs-store** endpoints
- **tcs-store** is independent (no downstream dependencies)

---

## Quick Test

Once all services are running:

```bash
# Test the full flow
cd tcs-api
poetry run pytest tests/test_full_integration.py -v
```

This will verify:
- Both services are accessible
- Save flow works end-to-end
- Validation is working
- Store persistence is working
- Filtering by trader works
