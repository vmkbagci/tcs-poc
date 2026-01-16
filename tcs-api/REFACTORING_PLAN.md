# Template System Refactoring Plan

## Overview

Based on the accurate JSON examples in `json-examples/polar/`, we need to refactor the template system to reflect the true structure of trades.

## Key Changes

### 1. Trade Structure Understanding

**OLD (Incorrect) Assumption:**
- All swaps have similar leg structures
- Variations are subtypes (vanilla, ois, basis, amortizing)
- Hierarchical inheritance: base → type → subtype → leg

**NEW (Correct) Structure:**
- Three distinct trade types with completely different economic blocks
- Shared administrative core (`general` + `common` blocks)
- Trade-specific economic blocks:
  - **IR Swap**: `swapDetails` + `swapLegs[]` array
  - **Commodity Option**: `commodityDetails` + `scheduleDetails` + `exercisePayment` + `premium`
  - **Index Swap**: `leg` object with nested structures

### 2. Template Architecture Changes

**OLD Directory Structure:**
```
templates/v1/
├── base/
│   ├── trade-base.json
│   ├── general-base.json
│   ├── swap-details-base.json
│   └── swap-leg-base.json
├── swap-types/
│   ├── irs/
│   │   ├── irs-base.json
│   │   ├── vanilla/
│   │   ├── ois/
│   │   ├── basis/
│   │   └── amortizing/
│   └── xccy/
├── leg-types/
│   ├── fixed-leg.json
│   ├── floating-ibor-leg.json
│   └── floating-ois-leg.json
└── conventions/
    ├── eur-conventions.json
    └── usd-conventions.json
```

**NEW Directory Structure:**
```
templates/v1/
├── core/
│   ├── general.json          # Shared by ALL trades
│   └── common.json           # Shared by ALL trades
└── trade-types/
    ├── ir-swap/
    │   ├── swap-details.json
    │   ├── swap-leg-fixed.json
    │   ├── swap-leg-floating-ois.json
    │   └── swap-leg-floating-ibor.json
    ├── commodity-option/
    │   ├── commodity-details.json
    │   ├── schedule-details.json
    │   ├── exercise-payment.json
    │   └── premium.json
    └── index-swap/
        ├── leg-base.json
        ├── underlying-asset.json
        ├── fixed-fee-leg.json
        ├── floating-index-leg.json
        └── payment.json
```

### 3. Factory Interface Changes

**OLD Interface:**
```python
factory.create_assembler(
    trade_type="irs",
    subtype="vanilla",
    currency="EUR",
    leg_configs=[
        {"type": "fixed", "legType": "Pay"},
        {"type": "floating-ibor", "legType": "Receive"}
    ]
)
```

**NEW Interface:**
```python
# IR Swap
factory.create_assembler(
    trade_type="ir-swap",
    leg_configs=[
        {"type": "fixed"},
        {"type": "floating-ois"}
    ]
)

# Commodity Option
factory.create_assembler(
    trade_type="commodity-option",
    exercise_type="europeanExercise",
    pricing_style="AVG_CMD_AVG_FX"
)

# Index Swap
factory.create_assembler(
    trade_type="index-swap",
    index_code="AIAGER",
    payment_ccy="USD"
)
```

## Refactoring Tasks

### Phase 1: Template Files (Task 2.4)
1. Create new directory structure
2. Create core templates (general.json, common.json)
3. Create IR Swap templates
4. Create Commodity Option templates
5. Create Index Swap templates
6. Remove old template files

### Phase 2: Factory Code (Task 2.5)
1. Refactor TradeTemplateFactory
2. Implement two-layer composition logic
3. Update component loading
4. Remove hierarchical inheritance logic
5. Update caching mechanism

### Phase 3: API Endpoint (Task 7.2)
1. Update /new endpoint parameters
2. Support three trade types
3. Update error handling
4. Update response format

### Phase 4: Testing (Task 2.8)
1. Test IR Swap creation
2. Test Commodity Option creation
3. Test Index Swap creation
4. Verify administrative core sharing
5. Verify economic block separation

## Benefits of Refactoring

1. **Accuracy**: Matches actual trade structure from production system
2. **Clarity**: Clear separation between shared and trade-specific components
3. **Simplicity**: No complex inheritance chains
4. **Extensibility**: Easy to add new trade types
5. **Maintainability**: Changes to core affect all trades, changes to trade-specific affect only that type

## Migration Notes

- Existing code in `src/trade_api/models/` needs refactoring
- Existing templates in `templates/v1/` need to be replaced
- API endpoint `/new` needs parameter updates
- No changes needed to Trade class or TradeAssembler (already correct)

## Next Steps

1. Review this refactoring plan with user
2. Analyze the three JSON files in detail to extract exact field structures
3. Begin implementing Phase 1 (template files)
4. Continue with Phase 2 (factory code)
5. Update Phase 3 (API endpoint)
6. Complete Phase 4 (testing)
