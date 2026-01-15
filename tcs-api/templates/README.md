# Trade Template Components

This directory contains hierarchical JSON components for trade template generation.

## Directory Structure

```
templates/
└── v1/                              # Template schema version
    ├── base/                        # Universal components (all trades)
    │   ├── trade-base.json          # Core trade fields
    │   ├── general-base.json        # Base general section
    │   └── swap-leg-base.json       # Base leg structure
    │
    ├── swap-types/                  # Trade type hierarchies
    │   ├── irs/                     # Interest Rate Swaps
    │   │   ├── irs-base.json        # Common to ALL IRS types
    │   │   ├── irs-leg-base.json    # Common to ALL IRS legs
    │   │   ├── vanilla/             # Vanilla IRS subtype
    │   │   │   ├── vanilla-irs.json
    │   │   │   └── vanilla-irs-legs.json
    │   │   ├── ois/                 # Overnight Index Swap
    │   │   ├── basis/               # Basis Swap
    │   │   └── amortizing/          # Amortizing IRS
    │   │
    │   └── xccy/                    # Cross Currency Swaps
    │       ├── xccy-base.json
    │       └── xccy-leg-base.json
    │
    ├── leg-types/                   # Leg-specific components
    │   ├── fixed-leg.json           # Fixed rate leg
    │   ├── floating-ibor-leg.json   # IBOR floating leg
    │   ├── floating-ois-leg.json    # OIS floating leg
    │   └── inflation-cpi-leg.json   # CPI inflation leg
    │
    └── conventions/                 # Market conventions
        ├── eur-conventions.json     # EUR market
        ├── usd-conventions.json     # USD market
        └── gbp-conventions.json     # GBP market
```

## Component Inheritance

Components are merged in hierarchical order (later overrides earlier):

### For Trade Structure:
1. `base/trade-base.json` - Universal trade fields
2. `base/general-base.json` - Universal general section
3. `swap-types/{type}/{type}-base.json` - Type-specific fields
4. `swap-types/{type}/{subtype}/{subtype}-{type}.json` - Subtype-specific fields
5. `conventions/{currency}-conventions.json` - Market-specific conventions

### For Each Leg:
1. `base/swap-leg-base.json` - Universal leg fields
2. `swap-types/{type}/{type}-leg-base.json` - Type-specific leg fields
3. `swap-types/{type}/{subtype}/{subtype}-{type}-legs.json` - Subtype-specific leg fields
4. `leg-types/{leg_type}-leg.json` - Leg-type-specific fields

## Example: Vanilla EUR IRS

For a Vanilla EUR IRS with Fixed + Floating legs:

**Trade Structure Components:**
1. `base/trade-base.json`
2. `base/general-base.json`
3. `swap-types/irs/irs-base.json`
4. `swap-types/irs/vanilla/vanilla-irs.json`
5. `conventions/eur-conventions.json`

**Fixed Leg Components:**
1. `base/swap-leg-base.json`
2. `swap-types/irs/irs-leg-base.json`
3. `swap-types/irs/vanilla/vanilla-irs-legs.json`
4. `leg-types/fixed-leg.json`

**Floating Leg Components:**
1. `base/swap-leg-base.json`
2. `swap-types/irs/irs-leg-base.json`
3. `swap-types/irs/vanilla/vanilla-irs-legs.json`
4. `leg-types/floating-ibor-leg.json`

## Schema Versioning

**Template Schema Version** (v1, v2, etc.):
- Defines the structure/format of templates
- Independent from trade business version
- Example: v1 uses `payerPartyCode`, v2 uses `payer`

**Trade Version** (1, 2, 3, etc.):
- Business version of a specific trade instance
- Incremented on amendments
- Completely independent from template schema version

A trade at version 5 can be created using template schema v1 or v2.

## Adding New Components

### Add New Trade Type:
1. Create directory: `swap-types/{new-type}/`
2. Add base file: `{new-type}-base.json`
3. Add leg base: `{new-type}-leg-base.json`
4. Add subtypes as needed

### Add New Subtype:
1. Create directory: `swap-types/{type}/{new-subtype}/`
2. Add subtype file: `{new-subtype}-{type}.json`
3. Add leg file: `{new-subtype}-{type}-legs.json`

### Add New Leg Type:
1. Create file: `leg-types/{new-leg-type}-leg.json`
2. Define leg-specific fields

### Add New Market:
1. Create file: `conventions/{currency}-conventions.json`
2. Define market-specific conventions

All additions are automatically discovered by `TradeTemplateFactory`!

## Benefits

1. **DRY Principle**: Change base component → all children inherit
2. **Clear Hierarchy**: Easy to see what each level adds
3. **Maintainability**: Modify once, affect all descendants
4. **Extensibility**: Add new types without code changes
5. **Version Control**: Track template changes in git
6. **Non-Developer Friendly**: JSON files can be edited by non-developers

## Usage

```python
from trade_api.models import TradeTemplateFactory

# Initialize factory with schema version
factory = TradeTemplateFactory(template_dir="templates", schema_version="v1")

# Create assembler for Vanilla EUR IRS
assembler = factory.create_assembler(
    trade_type="irs",
    subtype="vanilla",
    currency="EUR",
    leg_configs=[
        {"type": "fixed", "legType": "Pay"},
        {"type": "floating-ibor", "legType": "Receive"}
    ]
)

# Assemble trade dictionary
trade_dict = assembler.assemble()
```
