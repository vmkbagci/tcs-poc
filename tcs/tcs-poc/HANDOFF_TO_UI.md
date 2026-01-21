# Handoff to UI Team

**Date:** January 20, 2026  
**From:** Backend Integration Work  
**To:** UI Development Team

---

## Summary

The backend integration between **tcs-api** and **tcs-store** is complete and tested. All validation, save flows, and store integration are working. The UI can now be implemented to call the `/save` endpoint.

---

## What's Been Completed ✅

### 1. Trade Model Enhancement
- Added `trader` property to `ReadOnlyTrade` model
- Binds to `general.transactionRoles.priceMaker`
- Returns empty string if missing (safe default)

### 2. Validation Pipeline
- Added `priceMaker` to required fields in `CoreStructuralValidator`
- Field must exist (can be empty for presave, like tradeId)
- All validation tests passing (18/18)

### 3. API `/save` Endpoint
- Accepts context parameters: `user`, `agent`, `action`, `intent`
- Validates trade data using full validation pipeline
- Returns errors/warnings if validation fails
- Calls tcs-store `/save/new` if validation passes
- Returns success with trade data and metadata

### 4. Store Integration
- Created `StoreClient` HTTP client using httpx
- Handles store responses: 201 (success), 409 (duplicate), 422 (validation error), 503 (connection error)
- Transforms data between tcs-api and tcs-store formats

### 5. Integration Tests
- Created comprehensive test suite: `tcs-api/tests/test_full_integration.py`
- 5 test cases covering full flow, validation errors, duplicates, filtering
- Automation script: `run-integration-tests.sh`
- All tests passing ✅

### 6. Documentation
- Complete API examples: `tcs-api/examples/save_request_example.json`
- Integration progress: `INTEGRATION_PROGRESS.md`
- UI integration guide: `tcs-ui/UI_INTEGRATION_GUIDE.md`
- Service startup guide: `RUNNING_ALL_SERVICES.md`

---

## What UI Needs to Do

### 1. Create Trade Payload
- Generate trade JSON with all required fields
- Include `general.transactionRoles.priceMaker` (trader name)
- Set `tradeId` with "NEW" prefix for new trades
- Format: `NEW-YYYYMMDD-TYPE-SEQUENCE`

### 2. Call `/save` Endpoint
- **URL:** `POST http://localhost:5000/api/v1/trades/save`
- **Headers:** `Content-Type: application/json`
- **Body:**
  ```json
  {
    "user": "current_user_id",
    "agent": "tcs-ui",
    "action": "save_new",
    "intent": "new_trade_booking",
    "trade_data": { /* full trade JSON */ }
  }
  ```

### 3. Handle Responses
- **Success:** `response.success === true`
  - Display success message
  - Show trade ID from `response.trade_data.general.tradeId`
  - Store metadata if needed
- **Validation Error:** `response.success === false`
  - Display errors from `response.errors` array
  - Show warnings from `response.warnings` array
- **HTTP Error:** Status 4xx/5xx
  - Display error message to user

---

## Key Files for UI Team

### Documentation
- **`tcs-ui/UI_INTEGRATION_GUIDE.md`** ← START HERE
  - Complete integration guide with TypeScript examples
  - Request/response formats
  - Error handling
  - Testing instructions

- **`RUNNING_ALL_SERVICES.md`**
  - How to start all three services
  - Health check commands
  - Service dependencies

- **`INTEGRATION_PROGRESS.md`**
  - Complete backend work summary
  - API contract details
  - Architecture overview

### Example Files
- **`tcs-api/examples/save_request_example.json`**
  - Complete request/response examples
  - Success and error scenarios

- **`json-examples/polar/ir-swap-presave-flattened.json`**
  - Full trade JSON example
  - Shows all required fields

### Test Files
- **`tcs-api/tests/test_full_integration.py`**
  - Working examples of API calls
  - Shows how to construct requests
  - Demonstrates error handling

---

## Quick Start for UI Development

### 1. Start All Services

```bash
# Terminal 1: Store
cd tcs-store && ./run-store.sh

# Terminal 2: API
cd tcs-api && ./run-api.sh

# Terminal 3: UI
cd tcs-ui && npm start
```

### 2. Verify Services Running

```bash
curl http://localhost:5500/health  # Store
curl http://localhost:5000/health  # API
open http://localhost:4200         # UI
```

### 3. Test API Manually

```bash
curl -X POST http://localhost:5000/api/v1/trades/save \
  -H "Content-Type: application/json" \
  -d @tcs-api/examples/save_request_example.json
```

### 4. Run Integration Tests

```bash
./run-integration-tests.sh
```

---

## API Contract

### Request Format

```typescript
interface SaveTradeRequest {
  user: string;          // Required, non-empty
  agent: string;         // Required, non-empty (use "tcs-ui")
  action: string;        // Required, non-empty (e.g., "save_new")
  intent: string;        // Required, non-empty (e.g., "new_trade_booking")
  trade_data: {
    general: {
      tradeId: string;   // Must start with "NEW"
      transactionRoles: {
        priceMaker: string;  // REQUIRED field
      };
    };
    common: {
      book: string;
      tradeDate: string;
      counterparty: string;
      inputDate: string;
    };
    // ... product-specific sections
  };
}
```

### Response Format

```typescript
interface SaveTradeResponse {
  success: boolean;
  trade_data: any | null;
  errors: string[];
  warnings: string[];
  metadata: {
    documentId: string;
    correlationId: string;
    trade_type: string;
    validation_timestamp: string;
  } | null;
}
```

---

## Critical Fields

### Must Be Present in Trade Data

1. **`general.tradeId`** - Must start with "NEW" for new trades
2. **`general.transactionRoles.priceMaker`** - Trader name (REQUIRED)
3. **`common.book`** - Trading book
4. **`common.tradeDate`** - Trade date (YYYY-MM-DD)
5. **`common.counterparty`** - Counterparty ID
6. **`common.inputDate`** - Input date (YYYY-MM-DD)

### Must Be Present in Request

1. **`user`** - Current user ID
2. **`agent`** - Application ID (use "tcs-ui")
3. **`action`** - Operation type (e.g., "save_new")
4. **`intent`** - Business reason (e.g., "new_trade_booking")

---

## Testing Strategy

### 1. Unit Test UI Service
- Mock HTTP responses
- Test success/error handling
- Verify request format

### 2. Integration Test with Real API
- Start tcs-api and tcs-store
- Submit real trade data
- Verify response handling

### 3. End-to-End Test
- Create trade in UI
- Save via API
- Verify in store (call `/list` endpoint)

---

## Known Limitations

1. **Update Flow Not Implemented**
   - Only new trades supported (tradeId starts with "NEW")
   - Existing trade updates will return error

2. **No Retry Logic**
   - Network failures not automatically retried
   - UI should handle connection errors

3. **Trader Values**
   - Currently using: `["kbagci", "vmenon", "nseeley"]`
   - UI can use any trader ID

---

## Support Resources

### If API Returns Validation Errors
- Check that `priceMaker` field exists in `trade_data.general.transactionRoles`
- Verify all required fields are present
- Review `tcs-api/examples/save_request_example.json` for correct format

### If Connection Fails
- Verify tcs-api is running: `curl http://localhost:5000/health`
- Check tcs-store is running: `curl http://localhost:5500/health`
- Review logs: `tcs-api/api.log`

### If Tests Fail
- Run integration tests: `./run-integration-tests.sh`
- Check test output for specific failures
- Review `tcs-api/tests/test_full_integration.py` for working examples

---

## Next Steps

1. **Read:** `tcs-ui/UI_INTEGRATION_GUIDE.md`
2. **Start Services:** Use `RUNNING_ALL_SERVICES.md`
3. **Test API:** Use curl examples to verify API works
4. **Implement UI:**
   - Create trade form with trader field
   - Implement save service
   - Handle responses
5. **Test Integration:** Submit trade from UI, verify in store

---

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│         TCS-UI (Port 4200)              │
│  - Create trade with priceMaker         │
│  - Call /save with context              │
│  - Handle success/errors                │
└──────────────┬──────────────────────────┘
               │
               │ POST /api/v1/trades/save
               │ {user, agent, action, intent, trade_data}
               ▼
┌─────────────────────────────────────────┐
│        TCS-API (Port 5000)              │
│  1. Validate context                    │
│  2. Detect new trade                    │
│  3. Validate trade JSON                 │
│  4. Call tcs-store if valid             │
│  5. Return success/errors               │
└──────────────┬──────────────────────────┘
               │
               │ POST /save/new
               │ {context, trade: {id, data}}
               ▼
┌─────────────────────────────────────────┐
│       TCS-Store (Port 5500)             │
│  - Validate context                     │
│  - Check uniqueness                     │
│  - Store in memory                      │
│  - Return saved trade                   │
└─────────────────────────────────────────┘
```

---

## Contact

For questions about the backend implementation:
- Review integration tests: `tcs-api/tests/test_full_integration.py`
- Check API logs: `tcs-api/api.log`
- Review progress doc: `INTEGRATION_PROGRESS.md`

---

**Status:** ✅ Backend Ready - UI Can Begin Implementation

**Last Updated:** January 20, 2026
