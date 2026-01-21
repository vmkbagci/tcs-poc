# TCS Integration Tests

**Location:** `tcs-api/tests/test_full_integration.py`  
**Status:** ✅ All 5 tests passing

---

## Overview

These integration tests verify the complete flow from tcs-api to tcs-store, ensuring that:
- Services are accessible
- Trade validation works correctly
- Trades are saved to the store
- Trades can be retrieved and filtered
- Error handling works as expected

---

## Test Suite

### Test 1: `test_services_are_running`

**Purpose:** Verify both services are accessible before running tests

**What it does:**
- Checks tcs-api health endpoint: `GET http://localhost:5000/health`
- Checks tcs-store health endpoint: `GET http://localhost:5500/health`
- Skips all tests if services are not running

**Expected Result:** Both services return 200 OK

---

### Test 2: `test_full_save_and_list_flow` ⭐ Main Test

**Purpose:** Test the complete end-to-end flow

**What it does:**
1. Creates a trade payload with:
   - Trade ID: `NEW-20260120-IRSWAP-TEST-001`
   - Trader (priceMaker): `kbagci`
   - All required fields populated
2. Submits trade to tcs-api `/save` endpoint with context:
   - `user`: "trader_john"
   - `agent`: "pytest"
   - `action`: "save_new"
   - `intent`: "integration_test"
3. Verifies API response:
   - `success` is `true`
   - `errors` array is empty
   - `trade_data` is returned
   - `metadata` is present
4. Queries tcs-store `/list` endpoint with empty filter (all trades)
5. Verifies the saved trade appears in the list
6. Verifies trade data is correct:
   - Trade ID matches
   - Trader (priceMaker) is "kbagci"

**Expected Result:** 
```
✓ Trade saved via API: NEW-20260120-IRSWAP-TEST-001
✓ Found 1 trade(s) in store
✓ Trade verified in store with correct data
```

**Flow Diagram:**
```
Test → tcs-api /save → Validation → tcs-store /save/new → Store
Test → tcs-store /list → Verify trade exists
```

---

### Test 3: `test_save_with_validation_error`

**Purpose:** Verify that validation errors prevent storage

**What it does:**
1. Creates an invalid trade payload:
   - Missing `priceMaker` field (required)
   - Minimal structure (only general and common sections)
2. Submits to tcs-api `/save` endpoint
3. Verifies API response:
   - `success` is `false`
   - `errors` array contains validation error
   - `trade_data` is `null`
4. Queries tcs-store to verify trade was NOT saved

**Expected Result:**
```
✓ Validation error correctly returned: Unable to detect trade type
✓ Invalid trade not saved to store
```

**Key Point:** Validation happens BEFORE calling the store, preventing invalid data from being persisted.

---

### Test 4: `test_save_duplicate_trade`

**Purpose:** Verify duplicate trade ID handling

**What it does:**
1. Saves a trade with ID `NEW-20260120-IRSWAP-TEST-001`
2. Verifies first save succeeds
3. Attempts to save the same trade ID again
4. Verifies second save fails with duplicate error

**Expected Result:**
```
✓ First save succeeded
✓ Duplicate save correctly rejected: Trade with ID NEW-20260120-IRSWAP-TEST-001 already exists
```

**Key Point:** The store enforces trade ID uniqueness and returns a 409 Conflict error.

---

### Test 5: `test_filter_by_trader`

**Purpose:** Verify filtering trades by trader (priceMaker)

**What it does:**
1. Saves a trade with trader `vmenon`
2. Queries tcs-store `/list` with filter:
   ```json
   {
     "filter": {
       "data.general.transactionRoles.priceMaker": {"eq": "vmenon"}
     }
   }
   ```
3. Verifies only trades with trader "vmenon" are returned

**Expected Result:**
```
✓ Trade saved with trader: vmenon
✓ Filter by trader working: found 1 trade(s)
```

**Key Point:** The store supports filtering by nested fields using dot notation.

---

## Running the Tests

### Option 1: Use Automation Script (Recommended)

```bash
./run-integration-tests.sh
```

This script will:
- Check if services are running
- Start them if needed
- Run all tests
- Clean up services it started

### Option 2: Manual Execution

**Start services:**
```bash
# Terminal 1
cd tcs-store && ./run-store.sh

# Terminal 2
cd tcs-api && ./run-api.sh
```

**Run tests:**
```bash
cd tcs-api
poetry run pytest tests/test_full_integration.py -v
```

### Option 3: Run Individual Tests

```bash
cd tcs-api
poetry run pytest tests/test_full_integration.py::test_full_save_and_list_flow -v -s
```

---

## Test Configuration

**Service URLs:**
- tcs-api: `http://localhost:5000`
- tcs-store: `http://localhost:5500`

**Timeout:** 10 seconds per request

**Cleanup:** Each test cleans the store before and after execution

---

## Test Data

### Sample Trade Data

The tests use trade data from:
- `json-examples/polar/ir-swap-presave-flattened.json`

**Key fields:**
- `general.tradeId`: Modified to start with "NEW"
- `general.transactionRoles.priceMaker`: Set to specific trader
- `common.book`, `common.tradeDate`, `common.counterparty`, `common.inputDate`: All populated

### Context Data

```json
{
  "user": "trader_john",
  "agent": "pytest",
  "action": "save_new",
  "intent": "integration_test"
}
```

---

## Fixtures

### `check_services` (module scope)

Verifies both services are running before any tests execute. Skips all tests if services are unavailable.

### `cleanup_store` (function scope)

Purges the store before and after each test to ensure test isolation. Uses the `/admin/purge` endpoint.

### `sample_trade_data` (function scope)

Loads trade data from JSON file and ensures it has:
- Trade ID with "NEW" prefix
- priceMaker field populated

### `context` (function scope)

Provides context metadata for save operations.

---

## Expected Output

When all tests pass:

```
======================================================================================== test session starts =========================================================================================
platform linux -- Python 3.13.10, pytest-7.4.4, pluggy-1.6.0
collected 5 items

tests/test_full_integration.py::test_services_are_running PASSED                    [ 20%]
tests/test_full_integration.py::test_full_save_and_list_flow PASSED                 [ 40%]
tests/test_full_integration.py::test_save_with_validation_error PASSED              [ 60%]
tests/test_full_integration.py::test_save_duplicate_trade PASSED                    [ 80%]
tests/test_full_integration.py::test_filter_by_trader PASSED                        [100%]

========================================================================================= 5 passed in 0.34s ==========================================================================================
```

---

## Troubleshooting

### Tests Skipped - Services Not Running

**Error:** `SKIPPED (Services not running: [Errno 111] Connection refused)`

**Solution:**
1. Start tcs-store: `cd tcs-store && ./run-store.sh`
2. Start tcs-api: `cd tcs-api && ./run-api.sh`
3. Verify health: `curl http://localhost:5000/health`

### Test Failures Due to Store State

**Error:** Tests fail when run together but pass individually

**Solution:** The `cleanup_store` fixture should be function-scoped (not module-scoped) to clean between each test.

### Connection Timeout

**Error:** `httpx.TimeoutException`

**Solution:** 
- Check if services are responding slowly
- Increase timeout in test configuration
- Check service logs for errors

---

## What These Tests Prove

✅ **API Validation Works** - Invalid trades are rejected before reaching the store  
✅ **Store Integration Works** - API successfully calls store endpoints  
✅ **Data Persistence Works** - Trades are saved and can be retrieved  
✅ **Error Handling Works** - Validation errors and duplicates are handled correctly  
✅ **Filtering Works** - Store supports filtering by nested fields  
✅ **End-to-End Flow Works** - Complete flow from API to store is functional  

---

## Next Steps

With these tests passing, the backend is ready for UI integration. The UI can:

1. Create trade payloads with required fields
2. Call the `/save` endpoint with confidence
3. Handle success/error responses
4. Query the store to display saved trades

See `HANDOFF_TO_UI.md` and `tcs-ui/UI_INTEGRATION_GUIDE.md` for UI integration instructions.

---

**Last Updated:** January 21, 2026  
**Status:** ✅ All Tests Passing
