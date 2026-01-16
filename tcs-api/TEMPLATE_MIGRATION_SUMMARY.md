# Template Migration Summary

## Date: January 16, 2026

## Overview

Successfully migrated from hierarchical inheritance template structure to two-layer composition model based on accurate production JSON examples.

## Migration Steps Completed

### 1. Removed Old Template Structure ✅

**Deleted directories:**
- `templates/v1/base/` (3 files)
- `templates/v1/conventions/` (1 file)
- `templates/v1/leg-types/` (2 files)
- `templates/v1/swap-types/` (multiple subdirectories)

**Total files removed:** ~15+ old template files

### 2. Created New Two-Layer Structure ✅

**New directory structure:**
```
templates/v1/
├── core/                           # Layer 1: Administrative Core
│   ├── general.json                # Shared by ALL trades
│   └── common.json                 # Shared by ALL trades
│
└── trade-types/                    # Layer 2: Economic Blocks
    ├── ir-swap/
    │   ├── swap-details.json
    │   ├── swap-leg-fixed.json
    │   └── swap-leg-floating-ois.json
    │
    ├── commodity-option/
    │   ├── commodity-details.json
    │   ├── schedule-details.json
    │   ├── exercise-payment.json
    │   └── premium.json
    │
    └── index-swap/
        └── leg.json
```

## Template Files Created

### Layer 1: Administrative Core (2 files)

#### 1. `core/general.json`
**Purpose:** Shared general block for all trade types  
**Contains:**
- tradeId
- label
- transactionRoles (marketer, priceMaker, etc.)
- executionDetails (executionDateTime, venue, broker, etc.)
- packageTradeDetails
- blockAllocationDetails

**Source:** Extracted from `ir-swap-new-flattened.json`

#### 2. `core/common.json`
**Purpose:** Shared common block for all trade types  
**Contains:**
- book, counterparty, tradeDate
- Audit fields (inputDate, orderTime, comment)
- Operational flags (stp, ddeEligible, IRDAdvisory)
- Collections (events, fees, capitalSharing, tagMap, tradeIdentifiers)
- ISDADefinition

**Source:** Extracted from `ir-swap-new-flattened.json`

### Layer 2: Trade-Specific Economic Blocks (8 files)

#### IR Swap (3 files)

**1. `ir-swap/swap-details.json`**
- underlying, settlementType, swapType
- isCleared, markitSingleSided, principalExchange
- isIsdaFallback

**2. `ir-swap/swap-leg-fixed.json`**
- Fixed leg configuration
- legIndex: 0, direction: "pay", rateType: "fixed"
- formula: "ARR", dayCountBasis: "ACT/360"

**3. `ir-swap/swap-leg-floating-ois.json`**
- Floating OIS leg configuration
- legIndex: 1, direction: "receive", rateType: "floating"
- ratesetRef: "SOFR", referenceTenor: "1D"
- formula: "OIS", observationMethod: "plain", averagingMethod: "compound"

**Source:** Extracted from `ir-swap-new-flattened.json`

#### Commodity Option (4 files)

**1. `commodity-option/commodity-details.json`**
- optionExerciseType, settlementMethod, accumulation
- notionalVolume, strikeCurrency, strikeUnit, strikePayout
- pricingStyle: "AVG_CMD_AVG_FX"
- priceCalculation, assetPricing, fxFixing

**2. `commodity-option/schedule-details.json`**
- singleOrMultiPeriod, rollDirection, periodAlignOn
- frequency, pricingSchedule array

**3. `commodity-option/exercise-payment.json`**
- paymentCurrency, businessCenters
- payRelativeTo, paymentDaysOffset

**4. `commodity-option/premium.json`**
- priceUnits, deferredFlag, paymentStyle
- premiumValueDate, premiumFxRatesetDate

**Source:** Extracted from `commodity-option-new-flattened.json`

#### Index Swap (1 file)

**1. `index-swap/leg.json`**
- underlyingAsset (indexCode, ISIN)
- volume (volumeType, rounding)
- fixedFeeLeg (dayCountBasis, feeStartDate)
- floatingIndexLeg (periods, price, indexTradeDetails)
- payment (paymentCcy, assetCcy, paymentDaysOffset, calendar)

**Source:** Extracted from `index-swap-new-flattened.json`

## Key Differences: Old vs New

### Old Structure (Hierarchical Inheritance)
```
base → type → subtype → market → leg
```
- Assumed all swaps have similar structures
- Complex inheritance chains
- Focused on IRS variations (vanilla, ois, basis, amortizing)

### New Structure (Two-Layer Composition)
```
Layer 1: core (general + common) - shared by ALL
Layer 2: trade-types - completely different per type
```
- Three distinct trade types with different structures
- Clear separation of concerns
- Matches actual production data

## Template Usage Examples

### IR Swap Assembly
```python
components = [
    "core/general.json",
    "core/common.json",
    "trade-types/ir-swap/swap-details.json",
    {
        "swapLegs": [
            "trade-types/ir-swap/swap-leg-fixed.json",
            "trade-types/ir-swap/swap-leg-floating-ois.json"
        ]
    }
]
```

### Commodity Option Assembly
```python
components = [
    "core/general.json",
    "core/common.json",
    "trade-types/commodity-option/commodity-details.json",
    "trade-types/commodity-option/schedule-details.json",
    "trade-types/commodity-option/exercise-payment.json",
    "trade-types/commodity-option/premium.json"
]
```

### Index Swap Assembly
```python
components = [
    "core/general.json",
    "core/common.json",
    {
        "leg": "trade-types/index-swap/leg.json"
    }
]
```

## Next Steps

1. ✅ Old templates removed
2. ✅ New templates created
3. ⏳ Refactor TradeTemplateFactory to use new structure
4. ⏳ Update /new endpoint to support three trade types
5. ⏳ Test all three trade types
6. ⏳ Remove old factory code

## Verification

To verify the new structure:
```bash
ls -R tcs-api/templates/v1/
```

Expected output:
- 2 files in `core/`
- 3 files in `trade-types/ir-swap/`
- 4 files in `trade-types/commodity-option/`
- 1 file in `trade-types/index-swap/`

**Total: 10 template files**

## Benefits Achieved

1. ✅ **Accuracy**: Templates match actual production JSON structure
2. ✅ **Clarity**: Clear separation between shared and trade-specific components
3. ✅ **Simplicity**: No complex inheritance chains
4. ✅ **Extensibility**: Easy to add new trade types
5. ✅ **Maintainability**: Changes to core affect all trades, changes to trade-specific affect only that type

## Migration Complete

The template migration is complete. The new two-layer structure is ready for use with the refactored TradeTemplateFactory.
