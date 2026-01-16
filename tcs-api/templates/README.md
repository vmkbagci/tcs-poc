# Trade Template Components

⚠️ **REFACTORING IN PROGRESS**: This directory structure is being refactored to support three distinct trade types with a two-layer composition model. See `../REFACTORING_PLAN.md` for details.

## Current Status

The current implementation uses a hierarchical inheritance model that is being replaced with a two-layer composition model based on accurate production JSON examples.

## New Directory Structure (After Refactoring)

```
templates/
└── v1/                              # Template schema version
    ├── core/                        # Layer 1: Administrative Core (ALL trades)
    │   ├── general.json             # Shared general block
    │   └── common.json              # Shared common block
    │
    └── trade-types/                 # Layer 2: Economic Blocks (trade-specific)
        ├── ir-swap/                 # Interest Rate Swaps
        │   ├── swap-details.json
        │   ├── swap-leg-fixed.json
        │   ├── swap-leg-floating-ois.json
        │   └── swap-leg-floating-ibor.json
        │
        ├── commodity-option/        # Commodity Options
        │   ├── commodity-details.json
        │   ├── schedule-details.json
        │   ├── exercise-payment.json
        │   └── premium.json
        │
        └── index-swap/              # Index Swaps
            ├── leg-base.json
            ├── underlying-asset.json
            ├── fixed-fee-leg.json
            ├── floating-index-leg.json
            └── payment.json
```

## Two-Layer Composition Model

### Layer 1: Administrative Core
Shared by ALL trade types:
- `core/general.json` - Trade identification, execution details, package details
- `core/common.json` - Booking, counterparty, audit fields, fees, events

### Layer 2: Economic Blocks
Trade-specific structures:

**IR Swap:**
- `swapDetails` object
- `swapLegs[]` array with multiple legs

**Commodity Option:**
- `commodityDetails` object
- `scheduleDetails` object
- `exercisePayment` object
- `premium` object

**Index Swap:**
- `leg` object with nested structures:
  - `underlyingAsset`
  - `fixedFeeLeg`
  - `floatingIndexLeg`
  - `payment`

## Component Assembly Examples

### IR Swap (OIS)
```python
components = [
    # Layer 1: Administrative Core
    "core/general.json",
    "core/common.json",
    
    # Layer 2: IR Swap Economic Blocks
    "trade-types/ir-swap/swap-details.json",
    {
        "swapLegs": [
            "trade-types/ir-swap/swap-leg-fixed.json",
            "trade-types/ir-swap/swap-leg-floating-ois.json"
        ]
    }
]
```

### Commodity Option
```python
components = [
    # Layer 1: Administrative Core
    "core/general.json",
    "core/common.json",
    
    # Layer 2: Commodity Option Economic Blocks
    "trade-types/commodity-option/commodity-details.json",
    "trade-types/commodity-option/schedule-details.json",
    "trade-types/commodity-option/exercise-payment.json",
    "trade-types/commodity-option/premium.json"
]
```

### Index Swap
```python
components = [
    # Layer 1: Administrative Core
    "core/general.json",
    "core/common.json",
    
    # Layer 2: Index Swap Economic Block
    {
        "leg": merge(
            "trade-types/index-swap/leg-base.json",
            "trade-types/index-swap/underlying-asset.json",
            "trade-types/index-swap/fixed-fee-leg.json",
            "trade-types/index-swap/floating-index-leg.json",
            "trade-types/index-swap/payment.json"
        )
    }
]
```

## Schema Versioning

**Template Schema Version** (v1, v2, etc.):
- Defines the structure/format of templates
- Independent from trade business version
- Example: v1 uses certain field names, v2 might use different names

**Trade Version** (1, 2, 3, etc.):
- Business version of a specific trade instance
- Incremented on amendments
- Completely independent from template schema version

A trade at version 5 can be created using template schema v1 or v2.

## Adding New Components (After Refactoring)

### Add New Trade Type:
1. Create directory: `trade-types/{new-type}/`
2. Add economic block files specific to that trade type
3. Update factory to recognize new trade type

### Add Variations Within Trade Types:

**For IR Swaps:**
1. Create new leg template: `trade-types/ir-swap/swap-leg-{new-type}.json`

**For Commodity Options:**
1. Add new exercise type or pricing style templates

**For Index Swaps:**
1. Add new index-specific templates

## Benefits of New Architecture

1. **Clear Separation**: Administrative core vs economic blocks
2. **Trade Type Independence**: Each type has its own structure
3. **Maintainability**: Change core → affects all trades; change trade-specific → affects only that type
4. **Extensibility**: Add new types without affecting existing ones
5. **Accuracy**: Matches actual production trade structures

## Migration Status

- ❌ Old hierarchical templates (to be removed)
- ⏳ New two-layer templates (to be created)
- ⏳ Factory refactoring (in progress)
- ⏳ API endpoint updates (in progress)

See `../REFACTORING_PLAN.md` for complete migration plan and timeline.
