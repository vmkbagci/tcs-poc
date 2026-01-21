# Trade Field Configuration System

## Overview

The Trade Field Configuration System is a compositional architecture that determines which fields are visible in trade forms based on trade type. It uses a "Core + Trade-Specific" approach to avoid monolithic configurations and support multiple trade types efficiently.

---

## Core Concepts

### 1. Compositional Architecture

**Principle**: Configuration = Core Fields + Trade-Specific Fields

- **Core Fields**: Fields that exist in ALL trades of a given section (e.g., all trades have `tradeId`, `book`, `counterparty`)
- **Trade-Specific Fields**: Fields that only exist in certain trade types (e.g., IR Swaps have `principalExchange`, Commodity Swaps have `commodityType`)
- **Final Configuration**: Merged at runtime by combining core + trade-specific fields

**Why Compositional?**
- Avoids duplication (core fields defined once)
- Easy to add new trade types (just define trade-specific fields)
- Clear separation of concerns
- Scales well as trade types grow

### 2. Visibility Logic

**Simple Rule**: If a field exists in the configuration → it's visible. If it doesn't exist → it's not visible.

- No explicit `visible: true/false` flags needed
- No explicit `readonly: true/false` flags (can be added later if needed)
- Presence in config = visibility

### 3. Instance-Per-Trade

**Critical**: The service is NOT a singleton. Each trade gets its own configuration instance.

**Why?**
- Supports multiple trades open simultaneously in different browser tabs/windows
- Each trade can have different trade types
- No shared state conflicts

**Implementation**:
```typescript
@Component({
  providers: [TradeFieldConfigService]  // ← Creates new instance per component
})
export class TradeDetailComponent { }
```

---

## Architecture Diagram

```
TradeFieldConfigService (Instance per Trade)
│
├─ setTradeType('ir-swap')
│   └─ Triggers composition of configuration
│
├─ Composition Process:
│   ├─ General Section:
│   │   ├─ Core: [tradeId, label, coLocatedId, ...]
│   │   ├─ IR Swap Specific: [isPackageTrade, packageIdentifier, packageType]
│   │   └─ Merged: Core + IR Swap Specific
│   │
│   ├─ Common Section:
│   │   ├─ Core: [book, counterparty, tradeDate, ...]
│   │   ├─ Trade Specific: []
│   │   └─ Merged: Core only
│   │
│   ├─ SwapDetails Section:
│   │   ├─ Core: [underlying, settlementType, swapType, isCleared]
│   │   ├─ IR Swap Specific: [principalExchange, isIsdaFallback]
│   │   └─ Merged: Core + IR Swap Specific
│   │
│   ├─ SwapLegs Section:
│   │   ├─ Core: [direction, currency, rateType, notional, startDate, endDate]
│   │   ├─ Trade Specific: []
│   │   └─ Merged: Core only
│   │
│   └─ Schedule Section:
│       ├─ Core: [periodIndex, startDate, endDate, paymentDate, notional]
│       ├─ IR Swap Specific: [rate, interest, index]
│       └─ Merged: Core + IR Swap Specific
│
└─ Public API:
    ├─ hasField(section, field) → boolean
    ├─ isFieldRequired(section, field) → boolean
    ├─ getFieldConfig(section, field) → FieldConfig | null
    ├─ getSectionConfig(section) → SectionConfig | null
    └─ getFieldNames(section) → string[]
```

---

## Data Structures

### FieldConfig
```typescript
interface FieldConfig {
  fieldName: string;        // e.g., "tradeId"
  label: string;            // e.g., "Trade ID"
  required: boolean;        // Is this field required?
  placeholder?: string;     // Optional placeholder text
  helpText?: string;        // Optional help text
  validationRules?: ValidationRule[];  // Optional validation rules
}
```

### SectionConfig
```typescript
interface SectionConfig {
  sectionName: string;                    // e.g., "general"
  fields: Map<string, FieldConfig>;       // Map of field name → config
}
```

### TradeConfig
```typescript
interface TradeConfig {
  tradeType: string;                      // e.g., "ir-swap"
  sections: Map<string, SectionConfig>;   // Map of section name → config
}
```

---

## Sections and Their Purpose

### 1. General Section
**Purpose**: Core trade identification and execution details
**Applies to**: ALL trades
**Core Fields**: tradeId, label, coLocatedId, transactionRoles, executionDetails
**Trade-Specific Examples**:
- IR Swap: isPackageTrade, packageIdentifier, packageType
- Commodity Swap: isPackageTrade, packageIdentifier, commodityType
- Index Swap: indexIdentifier

### 2. Common Section
**Purpose**: Common trading information (book, counterparty, dates, references)
**Applies to**: ALL trades
**Core Fields**: book, counterparty, tradeDate, inputDate, comment, ISDADefinition
**Trade-Specific**: Currently none (all fields are core)

### 3. SwapDetails Section
**Purpose**: Swap-level configuration
**Applies to**: ALL swap trades (IR Swap, Commodity Swap, etc.)
**Core Fields**: underlying, settlementType, swapType, isCleared
**Trade-Specific Examples**:
- IR Swap: principalExchange, isIsdaFallback

### 4. SwapLegs Section
**Purpose**: Individual leg configuration
**Applies to**: ALL swap legs
**Core Fields**: direction, currency, rateType, notional, startDate, endDate
**Trade-Specific**: Currently none (all fields are core)

### 5. Schedule Section
**Purpose**: Schedule period details
**Applies to**: ALL schedules
**Core Fields**: periodIndex, startDate, endDate, paymentDate, notional
**Trade-Specific Examples**:
- IR Swap: rate, interest, index

---

## Usage in Components

### Step 1: Inject the Service
```typescript
@Component({
  providers: [TradeFieldConfigService]  // ← Instance per component
})
export class MyComponent {
  private fieldConfig = inject(TradeFieldConfigService);
}
```

### Step 2: Set Trade Type
```typescript
ngOnInit() {
  this.fieldConfig.setTradeType('ir-swap');
}
```

### Step 3: Check Field Visibility
```typescript
// In template
@if (hasField('underlying')) {
  <mat-form-field>
    <mat-label>Underlying</mat-label>
    <input matInput formControlName="underlying" />
  </mat-form-field>
}

// In component
hasField(fieldName: string): boolean {
  return this.fieldConfig.hasField('swapDetails', fieldName);
}
```

### Step 4: Check Field Requirements
```typescript
isRequired(fieldName: string): boolean {
  return this.fieldConfig.isFieldRequired('swapDetails', fieldName);
}
```

---

## Adding a New Trade Type

### Example: Adding "Commodity Swap"

**Step 1**: Define trade-specific fields in `getTradeSpecificGeneralFields()`
```typescript
case 'commodity-swap':
  return new Map([
    ['isPackageTrade', {
      fieldName: 'isPackageTrade',
      label: 'Is Package Trade',
      required: false
    }],
    ['packageIdentifier', {
      fieldName: 'packageIdentifier',
      label: 'Package Identifier',
      required: false
    }],
    ['commodityType', {
      fieldName: 'commodityType',
      label: 'Commodity Type',
      required: false
    }]
  ]);
```

**Step 2**: Add trade-specific fields for other sections as needed
```typescript
// In getTradeSpecificSwapDetailsFields()
case 'commodity-swap':
  return new Map([
    ['commodityGrade', {
      fieldName: 'commodityGrade',
      label: 'Commodity Grade',
      required: false
    }]
  ]);
```

**Step 3**: That's it! The service will automatically compose the configuration.

---

## Adding a New Field to All Trades

### Example: Adding "tradingDesk" to all trades

**Step 1**: Add to core fields in `getCoreCommonFields()`
```typescript
private getCoreCommonFields(): Map<string, FieldConfig> {
  return new Map([
    // ... existing fields ...
    ['tradingDesk', {
      fieldName: 'tradingDesk',
      label: 'Trading Desk',
      required: false
    }]
  ]);
}
```

**Step 2**: That's it! The field will now appear in ALL trades.

---

## Component Integration Pattern

### Pattern 1: Section Components (General, Common, SwapDetails)
```typescript
@Component({
  selector: 'app-general-section'
})
export class GeneralSectionComponent {
  private fieldConfig = inject(TradeFieldConfigService);

  // Check if field should be visible
  hasField(fieldName: string): boolean {
    return this.fieldConfig.hasField('general', fieldName);
  }

  // Check if field is required
  isRequired(fieldName: string): boolean {
    return this.fieldConfig.isFieldRequired('general', fieldName);
  }
}
```

### Pattern 2: Container Components (TradeDetail)
```typescript
@Component({
  providers: [TradeFieldConfigService]  // ← Provide instance
})
export class TradeDetailComponent {
  private fieldConfig = inject(TradeFieldConfigService);

  ngOnInit() {
    // Set trade type from route params
    this.route.queryParams.subscribe(params => {
      const tradeType = params['trade_type'] || 'ir-swap';
      this.fieldConfig.setTradeType(tradeType);
    });
  }
}
```

---

## Trade Type Examples

### IR Swap Configuration
```
General:
  Core: tradeId, label, coLocatedId, transactionRoles, executionDetails
  + IR Swap: isPackageTrade, packageIdentifier, packageType

Common:
  Core: book, counterparty, tradeDate, inputDate, comment, ISDADefinition

SwapDetails:
  Core: underlying, settlementType, swapType, isCleared
  + IR Swap: principalExchange, isIsdaFallback

SwapLegs:
  Core: direction, currency, rateType, notional, startDate, endDate

Schedule:
  Core: periodIndex, startDate, endDate, paymentDate, notional
  + IR Swap: rate, interest, index
```

### Commodity Swap Configuration (Example)
```
General:
  Core: tradeId, label, coLocatedId, transactionRoles, executionDetails
  + Commodity: isPackageTrade, packageIdentifier, commodityType

Common:
  Core: book, counterparty, tradeDate, inputDate, comment, ISDADefinition

SwapDetails:
  Core: underlying, settlementType, swapType, isCleared
  + Commodity: commodityGrade, deliveryLocation

SwapLegs:
  Core: direction, currency, rateType, notional, startDate, endDate

Schedule:
  Core: periodIndex, startDate, endDate, paymentDate, notional
  + Commodity: quantity, deliveryDate
```

---

## AI Agent Quick Reference

### For Understanding the System
```
PROMPT: "Explain how the trade field configuration system works"

KEY POINTS:
1. Compositional: Core + Trade-Specific = Final Config
2. Visibility: Field exists in config = visible
3. Instance-per-trade: Each trade gets own service instance
4. Sections: general, common, swapDetails, swapLegs, schedule
5. Service API: hasField(), isFieldRequired(), getFieldConfig()
```

### For Adding a New Trade Type
```
PROMPT: "Add a new trade type called [TRADE_TYPE]"

STEPS:
1. Identify trade-specific fields for each section
2. Add cases to getTradeSpecific*Fields() methods
3. Return Map of field name → FieldConfig
4. Service automatically composes with core fields
```

### For Adding a New Field to All Trades
```
PROMPT: "Add field [FIELD_NAME] to all trades in [SECTION]"

STEPS:
1. Add to getCore*Fields() method for the section
2. Add to Map with FieldConfig
3. Field automatically appears in all trades
```

### For Checking Field Visibility in Component
```
PROMPT: "How do I check if a field should be visible?"

CODE:
hasField(fieldName: string): boolean {
  return this.fieldConfig.hasField('sectionName', fieldName);
}

TEMPLATE:
@if (hasField('fieldName')) {
  <mat-form-field>...</mat-form-field>
}
```

### For Debugging Configuration
```
PROMPT: "Show me the configuration for [TRADE_TYPE]"

CODE:
const config = this.fieldConfig.getConfig();
console.log('Trade Type:', config?.tradeType);
console.log('Sections:', Array.from(config?.sections.keys() || []));
console.log('General Fields:', this.fieldConfig.getFieldNames('general'));
```

---

## Common Patterns

### Pattern: Conditional Field Display
```typescript
// In template
@if (hasField('principalExchange')) {
  <mat-form-field appearance="outline">
    <mat-label>Principal Exchange</mat-label>
    <mat-select formControlName="principalExchange">
      <mat-option value="none">None</mat-option>
      <mat-option value="firstLastLegs">First & Last Legs</mat-option>
    </mat-select>
  </mat-form-field>
}
```

### Pattern: Required Field Validation
```typescript
// In component
buildForm() {
  const validators = this.isRequired('tradeId') 
    ? [Validators.required] 
    : [];
  
  this.form = this.fb.group({
    tradeId: ['', validators]
  });
}
```

### Pattern: Dynamic Form Generation
```typescript
// Generate form fields dynamically
const fieldNames = this.fieldConfig.getFieldNames('general');
fieldNames.forEach(fieldName => {
  const config = this.fieldConfig.getFieldConfig('general', fieldName);
  if (config) {
    // Add field to form with appropriate validators
  }
});
```

---

## Best Practices

### DO:
✅ Use compositional approach (Core + Trade-Specific)
✅ Provide service at component level for instance-per-trade
✅ Check field visibility with `hasField()` before rendering
✅ Set trade type early in component lifecycle
✅ Use descriptive field names and labels

### DON'T:
❌ Make service a singleton (breaks multi-trade support)
❌ Hard-code field visibility in templates
❌ Duplicate core fields in trade-specific configs
❌ Forget to set trade type before using service
❌ Mix visibility logic with business logic

---

## Troubleshooting

### Problem: Field not showing up
**Check**:
1. Is field in core config for the section?
2. Is field in trade-specific config for the trade type?
3. Is trade type set correctly?
4. Is `hasField()` being called with correct section name?

### Problem: Wrong fields showing for trade type
**Check**:
1. Is correct trade type being set?
2. Are trade-specific fields defined for this trade type?
3. Is service instance being reused across different trades?

### Problem: Field showing in all trades when it shouldn't
**Check**:
1. Is field in core config? (Core = all trades)
2. Should it be in trade-specific config instead?

---

## File Locations

- **Service**: `tcs-ui/src/app/core/services/trade-field-config.service.ts`
- **Models**: `tcs-ui/src/app/core/models/`
- **Components**: `tcs-ui/src/app/features/*/components/`
- **Documentation**: `tcs-ui/docs/TRADE_FIELD_CONFIGURATION.md`

---

## Version History

- **v1.0** (2026-01-20): Initial compositional architecture
  - Core + Trade-Specific pattern
  - Instance-per-trade support
  - Five sections: general, common, swapDetails, swapLegs, schedule
  - IR Swap trade type implemented
