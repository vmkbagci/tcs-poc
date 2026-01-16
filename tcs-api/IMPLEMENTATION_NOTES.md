# Implementation Notes

## Current Status

### Completed Features

#### 1. Trade Class with JSON Composition (Task 2.1) ✓
- Implemented `Trade` class using orjson for fast JSON operations
- Uses jmespath for complex queries (filters, projections)
- Uses glom for nested property writes
- Implemented `ReadOnlyTrade` with cached properties and immutable data

#### 2. TradeAssembler for Component Composition (Task 2.3) ✓
- Deep merge capabilities with configurable list strategies
- Immutable operations using deepcopy
- Optional validation hooks and fluent API

#### 3. Hierarchical Template System (Task 2.4) ⚠️ NEEDS REFACTORING
- Created template directory structure with schema versioning (v1/)
- **NOTE**: Current implementation uses incorrect hierarchical inheritance model
- **REFACTORING NEEDED**: Switch to two-layer composition (administrative core + trade-specific economic blocks)
- See REFACTORING_PLAN.md for details

#### 4. TradeTemplateFactory (Task 2.5) ⚠️ NEEDS REFACTORING
- Hierarchical component inheritance implemented
- **NOTE**: Current implementation assumes all swaps have similar leg structures
- **REFACTORING NEEDED**: Support three distinct trade types (IR Swap, Commodity Option, Index Swap)
- See REFACTORING_PLAN.md for details

#### 5. /new GET Endpoint ⚠️ NEEDS REFACTORING
- Accepts 4 parameters: trade_type, trade_subtype, currency, leg_types
- Generates unique trade IDs (format: SWAP-YYYYMMDD-TYPE-SUBTYPE-NNNN)
- **NOTE**: Current implementation only supports IR Swap variations
- **REFACTORING NEEDED**: Support three trade types with different structures
- See REFACTORING_PLAN.md for details

### Endpoint Testing Results

⚠️ **NOTE**: Current implementation only supports IR Swap variations. Refactoring needed for Commodity Options and Index Swaps.

All IR Swap subtypes tested successfully:
- ✓ vanilla: Creates vanillaFixedFloat swap
- ✓ ois: Creates OIS swap
- ✓ basis: Creates basis swap
- ✓ amortizing: Creates amortizing swap

**Refactoring Required**: See REFACTORING_PLAN.md for details on supporting three distinct trade types.

### Known Issues and Design Decisions

#### 1. Lifecycle/LastEvent on Draft Creation (NOTED - NO CODE CHANGE)

**Issue**: The `/new` endpoint currently adds a `lastEvent` section to draft trades:
```json
{
  "lastEvent": {
    "version": 1,
    "correlationId": "...",
    "timestamp": "2026-01-14T23:53:28.054644Z",
    "intent": "BOOK_NEW_TRADE",
    "eventType": "Create",
    "executedBy": "",
    "platform": "TRADE_API",
    "comment": "New vanilla irswap template"
  }
}
```

**Design Concern**: Since `/new` creates a draft template (not persisted), the lifecycle should arguably start only when the trade is first saved/persisted via the `/save` endpoint.

**Current Behavior**: Draft templates include lifecycle metadata immediately.

**Recommended Future Behavior**:
- `/new` endpoint: Return template WITHOUT lastEvent section
- `/save` endpoint: Add initial lastEvent when trade is first persisted
- Subsequent saves: Update lastEvent with new version/timestamp

**Status**: NOTED - No code changes made. Will be addressed when implementing `/save` endpoint.

#### 2. Empty swapType for Non-Vanilla Subtypes

**Observation**: Only vanilla IRS has `swapType: "vanillaFixedFloat"`. Other subtypes (ois, basis, amortizing) have empty swapType.

**Reason**: Template files for ois, basis, and amortizing don't define swapType yet.

**Action Needed**: Update template files:
- `ois.json`: Add `"swapType": "ois"` or appropriate value
- `basis-swap.json`: Add `"swapType": "basis"` or appropriate value
- `amortizing-irs.json`: Add `"swapType": "amortizing"` or appropriate value

### Documentation Status

#### Requirements Document (requirements.md) ✓
- Contains all 6 requirements with EARS-formatted acceptance criteria
- Glossary defines all key terms
- User stories clearly stated

#### Design Document (design.md) ✓
- Architecture overview with component diagrams
- Trade class design with orjson/jmespath/glom
- TradeAssembler design
- **Template Factory Architecture section** - Comprehensive documentation of:
  - Hierarchical component system
  - Directory structure
  - Component inheritance chains
  - Example component files
  - Architectural benefits (DRY, maintainability, extensibility)
  - Use cases for adding fields and new types
  - Template schema versioning vs trade version
  - Performance considerations
- Correctness properties defined
- Testing strategy specified

#### Tasks Document (tasks.md) ✓
- Task 2.1 marked complete (Trade class)
- Task 2.3 implementation complete (TradeAssembler)
- Task 2.4 implementation complete (Template system)
- Task 2.5 implementation complete (TradeTemplateFactory)
- Partial progress on Task 7.2 (/new endpoint)

### API Endpoints

#### GET /api/v1/trades/new ✓
**Status**: Implemented and tested

**Parameters**:
- `trade_type` (required): "irswap", "xccy"
- `trade_subtype` (required): "vanilla", "ois", "basis", "amortizing"
- `currency` (optional, default "EUR"): Currency code
- `leg_types` (optional, default "fixed,floating-ibor"): Comma-separated leg types

**Response**: TradeResponse with assembled trade template

**Swagger UI**: http://127.0.0.1:8000/docs

#### POST /api/v1/trades/save
**Status**: Placeholder implementation

#### POST /api/v1/trades/validate
**Status**: Placeholder implementation

### Known Issues to Address

#### 2. Trade Data Missing Subtype Information (NOTED - TO BE FIXED)

**Issue**: The trade JSON returned by `/new` endpoint does not include the subtype information.

**Current Behavior**: Trade data contains:
```json
{
  "tradeType": "InterestRateSwap",
  "swapDetails": {
    "swapType": "vanillaFixedFloat",  // Only for vanilla, empty for others
    "currency": "EUR",
    ...
  }
}
```

**Missing**: No explicit field indicating the subtype (vanilla, ois, basis, amortizing)

**Recommended Solution**: Add subtype field to trade data, possibly:
- Option 1: Add `"subtype": "vanilla"` at top level
- Option 2: Add to swapDetails: `"subtype": "vanilla"`
- Option 3: Ensure swapType is properly populated for all subtypes

**Status**: NOTED - To be addressed before implementing `/validate` endpoint

**Rationale**: Validation logic may need to know the subtype to apply appropriate business rules

### Next Steps

**STOPPED AT**: Task 7.2 - /new endpoint implementation complete and tested (IR Swaps only)

**REFACTORING REQUIRED**: Template system needs to be refactored to support three distinct trade types:
1. **IR Swap**: swapDetails + swapLegs[] array
2. **Commodity Option**: commodityDetails + scheduleDetails + exercisePayment + premium
3. **Index Swap**: leg object with nested structures

See **REFACTORING_PLAN.md** for complete refactoring strategy.

**NEXT SESSION**: Refactor template system (Tasks 2.4, 2.5, 7.2)

**Before continuing**:
1. **Fix subtype information** - Add subtype field to trade data
2. **Address lifecycle issue** - Remove lastEvent from draft trades
3. **Update template files** - Add swapType for ois, basis, amortizing

**Then proceed with**:
1. **Implement /validate endpoint** with validation pipeline
2. **Implement /save endpoint** with proper lifecycle management
3. **Add property-based tests** for implemented components
4. **Add unit tests** for edge cases

### Template Schema Version vs Trade Version

**Important Distinction** (documented in design.md):
- **Template Schema Version**: Format/structure of templates (v1, v2, etc.)
  - Example: v1 uses `payerPartyCode`, v2 might use `payer`
  - Stored in: `templates/v1/`, `templates/v2/`
  - Changed when template structure changes
  
- **Trade Version**: Business version of specific trade instance (1, 2, 3, etc.)
  - Example: Trade starts at version 1, increments on amendments
  - Stored in: `trade.version` field
  - Changed when trade is amended/updated

These are completely independent concepts. A trade at version 5 can be created using template schema v1 or v2.

### Server Information

**Running**: Yes (Process ID: 12)
**URL**: http://127.0.0.1:8000
**Swagger UI**: http://127.0.0.1:8000/docs
**Auto-reload**: Enabled
