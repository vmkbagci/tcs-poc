# TCS-UI Integration Guide

**Date:** January 20, 2026  
**Status:** Ready for UI Implementation

This guide provides everything the UI team needs to integrate with the tcs-api `/save` endpoint.

---

## Overview

The backend (tcs-api + tcs-store) is fully implemented and tested. The UI needs to:

1. Create trade payloads with required fields (including `priceMaker`)
2. Call the `/save` endpoint with context parameters
3. Handle success/error responses

---

## API Endpoint

### Save Trade

**Endpoint:** `POST http://localhost:5000/api/v1/trades/save`

**Content-Type:** `application/json`

---

## Request Format

### TypeScript Interface

```typescript
interface SaveTradeRequest {
  // Context parameters (all required)
  user: string;          // User ID or service account
  agent: string;         // Application identifier (use "tcs-ui")
  action: string;        // Operation being performed (e.g., "save_new")
  intent: string;        // Business reason (e.g., "new_trade_booking")
  
  // Trade data
  trade_data: {
    general: {
      tradeId: string;   // Must start with "NEW" for new trades
      transactionRoles: {
        priceMaker: string;  // REQUIRED - trader name
        // ... other roles
      };
      // ... other general fields
    };
    common: {
      book: string;
      tradeDate: string;
      counterparty: string;
      inputDate: string;
      // ... other common fields
    };
    // ... product-specific sections (swapDetails, swapLegs, etc.)
  };
}
```

### Example Request

```json
{
  "user": "trader_john",
  "agent": "tcs-ui",
  "action": "save_new",
  "intent": "new_trade_booking",
  "trade_data": {
    "general": {
      "tradeId": "NEW-20260120-IRSWAP-1234",
      "transactionRoles": {
        "priceMaker": "kbagci"
      }
    },
    "common": {
      "book": "RATES_DESK_001",
      "tradeDate": "2026-01-20",
      "counterparty": "BANK_A",
      "inputDate": "2026-01-20"
    }
  }
}
```

---

## Response Format

### TypeScript Interface

```typescript
interface SaveTradeResponse {
  success: boolean;
  trade_data: any | null;      // Full trade data if successful
  errors: string[];            // Error messages if failed
  warnings: string[];          // Warning messages (non-blocking)
  metadata: {
    documentId: string;        // UUID v4
    correlationId: string;     // UUID v4
    trade_type: string;        // e.g., "ir-swap"
    validation_timestamp: string;  // ISO 8601
  } | null;
}
```

### Success Response (200 OK)

```json
{
  "success": true,
  "trade_data": {
    "general": { "tradeId": "NEW-20260120-IRSWAP-1234", ... },
    "common": { ... },
    "swapDetails": { ... },
    "swapLegs": [ ... ]
  },
  "errors": [],
  "warnings": [],
  "metadata": {
    "documentId": "6e80b8aa-38ed-4397-965a-5536b3a4dcbd",
    "correlationId": "7c3d9e2f-1a4b-5c6d-e8f9-0a1b2c3d4e5f",
    "trade_type": "ir-swap",
    "validation_timestamp": "2026-01-20T10:30:45.123456"
  }
}
```

### Validation Error Response (200 OK, success=false)

```json
{
  "success": false,
  "trade_data": null,
  "errors": [
    "Required field missing: general.transactionRoles.priceMaker"
  ],
  "warnings": [],
  "metadata": {
    "documentId": "6e80b8aa-38ed-4397-965a-5536b3a4dcbd",
    "correlationId": "7c3d9e2f-1a4b-5c6d-e8f9-0a1b2c3d4e5f",
    "trade_type": "ir-swap",
    "validation_timestamp": "2026-01-20T10:30:45.123456"
  }
}
```

### HTTP Error Response (4xx/5xx)

```json
{
  "detail": "Error message here"
}
```

---

## Required Fields

### Context Parameters (Request Level)

All context parameters are **required** and must be **non-empty strings**:

- `user` - Current user identifier
- `agent` - Should be `"tcs-ui"` for UI requests
- `action` - Operation type (e.g., `"save_new"`)
- `intent` - Business reason (e.g., `"new_trade_booking"`)

### Trade Data Fields

**Critical fields that must be present:**

1. **Trade ID** (`trade_data.general.tradeId`)
   - Must start with `"NEW"` for new trades
   - Format: `NEW-YYYYMMDD-TYPE-SEQUENCE`
   - Example: `"NEW-20260120-IRSWAP-1234"`

2. **Trader** (`trade_data.general.transactionRoles.priceMaker`)
   - **REQUIRED** - Must exist in the structure
   - Can be empty string for presave payloads
   - Should be populated with actual trader name
   - Valid values: `"kbagci"`, `"vmenon"`, `"nseeley"` (or any trader ID)

3. **Common Fields** (`trade_data.common`)
   - `book` - Trading book
   - `tradeDate` - Trade date (YYYY-MM-DD)
   - `counterparty` - Counterparty identifier
   - `inputDate` - Input date (YYYY-MM-DD)

---

## Implementation Example (Angular)

### Service Method

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class TradeService {
  private apiUrl = 'http://localhost:5000/api/v1/trades';

  constructor(private http: HttpClient) {}

  saveTrade(
    tradeData: any,
    user: string,
    action: string = 'save_new',
    intent: string = 'new_trade_booking'
  ): Observable<SaveTradeResponse> {
    const request: SaveTradeRequest = {
      user: user,
      agent: 'tcs-ui',
      action: action,
      intent: intent,
      trade_data: tradeData
    };

    return this.http.post<SaveTradeResponse>(
      `${this.apiUrl}/save`,
      request
    );
  }
}
```

### Component Usage

```typescript
export class TradeFormComponent {
  constructor(private tradeService: TradeService) {}

  onSave() {
    const tradeData = {
      general: {
        tradeId: this.generateTradeId(),
        transactionRoles: {
          priceMaker: this.selectedTrader  // From dropdown/input
        }
      },
      common: {
        book: this.form.value.book,
        tradeDate: this.form.value.tradeDate,
        counterparty: this.form.value.counterparty,
        inputDate: new Date().toISOString().split('T')[0]
      }
      // ... rest of trade data
    };

    this.tradeService.saveTrade(
      tradeData,
      this.currentUser,
      'save_new',
      'new_trade_booking'
    ).subscribe({
      next: (response) => {
        if (response.success) {
          this.showSuccess('Trade saved successfully!');
          console.log('Trade ID:', response.trade_data.general.tradeId);
          console.log('Metadata:', response.metadata);
        } else {
          this.showErrors(response.errors);
        }
      },
      error: (error) => {
        this.showError('Failed to save trade: ' + error.message);
      }
    });
  }

  private generateTradeId(): string {
    const date = new Date().toISOString().split('T')[0].replace(/-/g, '');
    const sequence = Math.floor(Math.random() * 10000);
    return `NEW-${date}-IRSWAP-${sequence}`;
  }
}
```

---

## Error Handling

### Response Status Codes

- **200 OK** - Request processed (check `success` field)
  - `success: true` - Trade saved successfully
  - `success: false` - Validation failed (see `errors` array)
- **422 Unprocessable Entity** - Invalid request format (missing context params)
- **500 Internal Server Error** - Server error

### Error Display

```typescript
showErrors(errors: string[]) {
  if (errors.length === 0) return;
  
  // Display errors to user
  const errorMessage = errors.join('\n');
  this.notificationService.error('Validation Failed', errorMessage);
  
  // Or display inline in form
  this.validationErrors = errors;
}
```

---

## Validation Rules

The API validates:

1. **Context Parameters**
   - All must be present
   - All must be non-empty strings
   - Missing/empty → 422 error

2. **Trade Structure**
   - `general.tradeId` must exist
   - `general.transactionRoles.priceMaker` must exist (can be empty)
   - `common.book`, `common.tradeDate`, `common.counterparty`, `common.inputDate` must exist

3. **Trade ID Format**
   - New trades must have ID starting with `"NEW"`
   - Existing trade updates not yet implemented

---

## Testing the Integration

### 1. Start Services

```bash
# Terminal 1: Start tcs-store
cd tcs-store
./run-store.sh

# Terminal 2: Start tcs-api
cd tcs-api
./run-api.sh

# Terminal 3: Start tcs-ui
cd tcs-ui
npm start
```

### 2. Test with curl

```bash
curl -X POST http://localhost:5000/api/v1/trades/save \
  -H "Content-Type: application/json" \
  -d '{
    "user": "test_user",
    "agent": "tcs-ui",
    "action": "save_new",
    "intent": "test",
    "trade_data": {
      "general": {
        "tradeId": "NEW-20260120-TEST-001",
        "transactionRoles": {
          "priceMaker": "kbagci"
        }
      },
      "common": {
        "book": "TEST_BOOK",
        "tradeDate": "2026-01-20",
        "counterparty": "TEST_CP",
        "inputDate": "2026-01-20"
      }
    }
  }'
```

### 3. Verify in Store

```bash
curl -X POST http://localhost:5500/list \
  -H "Content-Type: application/json" \
  -d '{"filter": {}}'
```

---

## Common Issues

### Issue: 422 Error - Missing Context

**Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "user"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Solution:** Ensure all context parameters are included in request.

---

### Issue: Validation Failed - Missing priceMaker

**Response:**
```json
{
  "success": false,
  "errors": ["Required field missing: general.transactionRoles.priceMaker"]
}
```

**Solution:** Add `priceMaker` field to `trade_data.general.transactionRoles`.

---

### Issue: Connection Refused

**Error:** `Failed to connect to http://localhost:5000`

**Solution:** 
1. Check if tcs-api is running: `curl http://localhost:5000/health`
2. Start tcs-api: `cd tcs-api && ./run-api.sh`

---

## Next Steps for UI

1. **Create Trade Form**
   - Add trader dropdown/input field
   - Bind to `priceMaker` field
   - Generate trade ID with "NEW" prefix

2. **Implement Save Service**
   - Use example code above
   - Add error handling
   - Display success/error messages

3. **Test Integration**
   - Start all services
   - Create and save a trade
   - Verify it appears in store

4. **Add Trade List View**
   - Call tcs-store `/list` endpoint directly
   - Display saved trades
   - Filter by trader

---

## Reference Files

- **API Implementation:** `tcs-api/src/trade_api/api/trades.py`
- **Service Logic:** `tcs-api/src/trade_api/services/trade_service.py`
- **Store Client:** `tcs-api/src/trade_api/clients/store_client.py`
- **Integration Tests:** `tcs-api/tests/test_full_integration.py`
- **Example Request:** `tcs-api/examples/save_request_example.json`
- **Progress Doc:** `INTEGRATION_PROGRESS.md`

---

## Support

If you encounter issues:

1. Check service health endpoints
2. Review integration tests for working examples
3. Check API logs: `tcs-api/api.log`
4. Run integration tests: `./run-integration-tests.sh`

---

**Ready to integrate!** The backend is fully functional and tested.
