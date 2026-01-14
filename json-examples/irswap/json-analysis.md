# Interest Rate Swap JSON Structure Analysis

## Overview

This document analyzes the JSON structure of Interest Rate Swap (IRS) trades found in the `json-examples/irswap` folder. The analysis identifies common fields, unique fields, structural patterns, and variations across different swap subtypes.

## Dataset Summary

**Total Files Analyzed**: 13 swap examples

**Swap Subtypes Identified**:
1. Vanilla Fixed-Float IRS (4 examples: EUR, GBP, USD, original)
2. Overnight Index Swap (OIS)
3. Basis Swap (Float-Float)
4. Forward-Starting IRS
5. Amortizing IRS
6. Zero-Coupon Swap
7. Nonstandard IRS
8. CPI Inflation Swap
9. Year-on-Year Inflation Swap
10. Digital CMS Spread Swap

## Common Fields (Present in ALL trades)

### Top-Level Fields
All trades share these mandatory top-level fields:

```json
{
  "tradeId": "UUID",
  "tradeExtId": "External system identifier",
  "label": "Descriptive label",
  "version": "Integer version number",
  "tradeType": "InterestRateSwap",
  "status": "Trade status (Confirmed/Abandoned)",
  "lastEvent": { ... },
  "general": { ... },
  "swapDetails": { ... },
  "swapLegs": [ ... ]
}
```


### lastEvent Structure (Common)
Every trade tracks its lifecycle with a `lastEvent` object:

```json
"lastEvent": {
  "version": 1,
  "correlationId": "UUID",
  "timestamp": "ISO 8601 timestamp",
  "intent": "BOOK_NEW_TRADE | AMEND_ECONOMICS | CANCEL_TRADE",
  "eventType": "Create | Amend | Cancel",
  "executedBy": "User ID",
  "platform": "System name",
  "comment": "Human-readable description"
}
```

### general.common Structure (Common)
All trades have these common general fields:

```json
"general": {
  "common": {
    "book": "Trading book identifier",
    "tradeDate": "YYYY-MM-DD",
    "counterparty": "Counterparty code",
    "ddeEligible": "Yes | No",
    "includeFeeEngine": "none | standard",
    "isdaDefinition": "ISDA2021"
  }
}
```

### general.transactionInformation (Common)
Transaction metadata present in all trades:

```json
"transactionInformation": {
  "roles": {
    "transactionOriginator": "User ID",
    "priceMaker": "User ID",
    "transactionAcceptor": "User ID",
    "marketer": null,
    "parameterGrantor": null
  },
  "executionDetails": {
    "executionDateTime": "ISO 8601 timestamp",
    "executionVenueType": "OffFacility | OnFacility",
    "isOffMarketPrice": false
  }
}
```


### general.parties (Common)
All trades define participating parties:

```json
"parties": [
  {
    "code": "Party code",
    "lei": "Legal Entity Identifier",
    "name": "Full legal name",
    "role": "Dealer | Client | ExecutingBroker"
  }
]
```

### swapLegs Structure (Common)
All swaps have 1-2 legs with common structure:

```json
"swapLegs": [
  {
    "legType": "Pay | Receive",
    "payerPartyCode": "Party code",
    "receiverPartyCode": "Party code",
    "currency": "ISO currency code",
    "rateType": "fixed | floating | zeroCouponFixed | cpi | yoyInflation | digitalCmsSpread",
    "notional": "Numeric amount",
    "pricing": { ... },
    "schedule": {
      "frequency": "annual | semiannual | quarterly | bullet",
      "startDate": "YYYY-MM-DD",
      "endDate": "YYYY-MM-DD",
      "periods": [ ... ]
    }
  }
]
```

## Unique/Optional Fields by Subtype

### 1. Vanilla Fixed-Float IRS

Vanilla IRS is the most common swap type with **4 examples** showing different field variations:

#### Common Vanilla IRS Fields:
- `swapDetails.swapType` - "vanillaFixedFloat" or "irs"
- `swapDetails.currency` - Currency code
- `swapDetails.underlying` - Reference index (e.g., "EUR-EURIBOR-6M")
- Two legs: one fixed, one floating

#### Variation A: Original Vanilla IRS (`vanilla-irs.json`)
**Unique Fields**:
- `general.identifiers` - External scheme identifiers
- `swapDetails.conventions.settlementDays` - Settlement lag
- `swapDetails.conventions.dateGenerationRule` - "Backward" | "Forward"
- `swapDetails.conventions.endOfMonth` - Boolean flag
- `swapDetails.conventions.calendar` - "TARGET"
- `swapDetails.conventions.fixedLegTenor` - "1Y"
- `swapDetails.conventions.floatingLegTenor` - "6M"
- `swapLegs[].schedule.periods[]` - Explicit period definitions with dates

#### Variation B: EUR Vanilla IRS (`eur-vanilla-irs.json`)
**Unique Fields**:
- `general.envelope` - Organizational metadata
  - `counterparty` - Counterparty code
  - `nettingSetId` - Netting set identifier
  - `portfolioIds` - Array of portfolio IDs
  - `additionalFields` - Flexible key-value pairs (Desk, Book, Sector, Strategy)
- `parties` - Top-level array (not nested in `general`)
- `swapLegs[].payer` - Party code (instead of `payerPartyCode`)
- `swapLegs[].receiver` - Party code (instead of `receiverPartyCode`)
- `swapLegs[].schedule.frequency` - ISO 8601 duration format ("P1Y", "P6M")
- `swapLegs[].pricing.referenceTenor` - Explicit tenor on floating leg

#### Variation C: GBP Vanilla IRS (`gbp-vanilla-irs.json`)
**Unique Fields**:
- `general.regulatoryIdentifiers` - Regulatory reporting identifiers
  - `uti` - Unique Transaction Identifier
  - `upi` - Unique Product Identifier
  - `reportingRegime` - "UK" | other
  - `tradeRepository` - Trade repository name
- `parties` - Top-level array (not nested in `general`)
- `swapLegs[].payer` / `swapLegs[].receiver` - Simplified party references
- `swapLegs[].schedule.frequency` - ISO 8601 duration format
- `valuationSnapshot` - Optional valuation data
  - `pricingEngine` - Engine name
  - `valuationTimestamp` - Valuation time
  - `fairRate` - Fair market rate
  - `npv` - Net present value
  - `currency` - Valuation currency

#### Variation D: USD Vanilla IRS (`usd-vanilla-irs.json`)
**Unique Fields**:
- `general.sourceIdentifiers` - Source system identifiers
  - `scheme` - Source scheme (e.g., "OG")
  - `id` - Source ID
- `parties` - Top-level array
- `swapLegs[].payer` / `swapLegs[].receiver` - Simplified party references
- `swapLegs[].schedule.frequency` - ISO 8601 duration format
- `swapLegs[].schedule.rollConvention` - "Day1" | other
- `swapLegs[].schedule.stubConvention` - "ShortInitial" | other
- `swapLegs[].schedule.paymentRelativeTo` - "PeriodEnd" | "PeriodStart"
- `swapLegs[].schedule.paymentOffset` - Complex payment offset structure
  - `days` - Offset days
  - `calendar` - Calendar code
  - `adjustmentConvention` - "Following" | other
  - `adjustmentCalendar` - Adjustment calendar
- `swapLegs[].pricing.fixingRelativeTo` - "PeriodStart" | "PeriodEnd"
- `swapLegs[].pricing.fixingOffset` - Complex fixing offset structure (same as paymentOffset)
- `swapLegs[].pricing.resetFrequency` - Reset frequency
- `swapLegs[].pricing.resetMethod` - "Weighted" | other
- `swapLegs[].pricing.negativeRateMethod` - "AllowNegative"

**Key Observation**: Vanilla IRS shows the most structural variation, with 4 different field naming conventions:
1. Original: `payerPartyCode`/`receiverPartyCode`, explicit periods array
2. EUR/GBP/USD: `payer`/`receiver`, ISO 8601 frequency format
3. EUR: Adds `envelope` with netting/portfolio metadata
4. GBP: Adds `regulatoryIdentifiers` and `valuationSnapshot`
5. USD: Adds detailed `paymentOffset` and `fixingOffset` structures


### 2. Overnight Index Swap (OIS)
**Unique Fields**:
- `swapDetails.oisConventions.paymentLagDays` - Payment lag
- `swapDetails.oisConventions.telescopicValueDates` - Boolean
- `swapDetails.oisConventions.paymentAdjustment` - "Following" | other
- `swapLegs[].pricing.referenceTenor` - "1D" for overnight
- `swapLegs[].pricing.accrualMethod` - "Compounded"
- `swapLegs[].pricing.rateCutOffDays` - Cut-off period
- `swapLegs[].pricing.negativeRateMethod` - "AllowNegative"
- `swapLegs[].pricing.style` - "overnight"

**Example**: `ois.json`

### 3. Basis Swap (Float-Float)
**Unique Fields**:
- `swapDetails.basis.index1` - First floating index
- `swapDetails.basis.index2` - Second floating index
- `swapLegs[].pricing.fixingRelativeTo` - "PeriodStart" | "PeriodEnd"
- `swapLegs[].pricing.fixingOffsetDays` - Fixing lag
- `swapLegs[].pricing.resetFrequency` - Reset frequency
- `swapLegs[].pricing.resetMethod` - "Weighted" | other

**Example**: `basis-swap.json`

### 4. Forward-Starting IRS
**Unique Fields**:
- `swapDetails.conventions.forwardStart` - ISO 8601 duration (e.g., "P2D")
- `swapDetails.conventions.effectiveDateOverride` - Explicit start date
- `swapDetails.conventions.terminationDateOverride` - Explicit end date
- `general.transactionInformation.executionDetails.executionVenueMIC` - Market identifier code
- Additional party with `role: "ExecutingBroker"`

**Example**: `forward-starting-irs.json`


### 5. Amortizing IRS
**Unique Fields**:
- `swapDetails.amortization.type` - "stepDown" | "stepUp"
- `swapDetails.amortization.notionalSchedule` - Array of notional changes
  ```json
  [
    { "effective": "YYYY-MM-DD", "notional": amount },
    ...
  ]
  ```
- `swapLegs[].schedule.periods[].notional` - Per-period notional amounts

**Example**: `amortizing-irs.json`

### 6. Zero-Coupon Swap
**Unique Fields**:
- `general.envelope` - Additional organizational metadata
  - `nettingSetId` - Netting set identifier
  - `portfolioIds` - Array of portfolio identifiers
  - `additionalFields` - Flexible key-value pairs
- `swapLegs[].rateType` - "zeroCouponFixed"
- `swapLegs[].pricing.rates` - Array of rates
- `swapLegs[].pricing.compounding` - "Simple" | "Continuous"
- `swapLegs[].schedule.frequency` - "bullet" (single payment)
- `swapLegs[].schedule.periods[].paymentDate` - Explicit payment date

**Example**: `zero-coupon-swap.json`

### 7. Nonstandard IRS
**Unique Fields**:
- `swapDetails.notionalExchange.intermediateCapitalExchange` - Boolean
- `swapDetails.notionalExchange.finalCapitalExchange` - Boolean
- `swapLegs[].pricing.interestRateSchedulePct` - Array of rates per period
- `swapLegs[].pricing.gearings` - Array of multipliers per period
- `swapLegs[].pricing.spreadsBps` - Array of spreads per period

**Example**: `nonstandard-irs.json`


### 8. CPI Inflation Swap
**Unique Fields**:
- `general.envelope` - Organizational metadata (similar to zero-coupon)
- `swapLegs[].rateType` - "cpi"
- `swapLegs[].pricing.index` - "UKRPI" | other inflation index
- `swapLegs[].pricing.fixedRate` - Fixed inflation rate
- `swapLegs[].pricing.baseCpi` - Base CPI value
- `swapLegs[].pricing.observationLag` - "2M" | other lag period
- `swapLegs[].pricing.interpolated` - Boolean
- `swapLegs[].pricing.subtractInflationNotional` - Boolean

**Example**: `cpi-swap.json`

### 9. Year-on-Year Inflation Swap
**Unique Fields**:
- `general.envelope` - Organizational metadata
- `swapLegs[].rateType` - "yoyInflation"
- `swapLegs[].pricing.index` - "EUCPI" | other inflation index
- `swapLegs[].pricing.fixingDays` - "2D" | other fixing lag
- `swapLegs[].pricing.observationLag` - "3M" | other lag period
- `swapLegs[].pricing.caps` - Array of cap rates
- `swapLegs[].pricing.floors` - Array of floor rates

**Example**: `year-on-year-inflation-swap.json`

### 10. Digital CMS Spread Swap
**Unique Fields**:
- `status` - "Abandoned" (example of non-Confirmed status)
- `general.envelope` - Organizational metadata
- `general.transactionInformation.executionDetails.isOffMarketPrice` - true
- `swapLegs[].rateType` - "digitalCmsSpread"
- `swapLegs[].pricing.index1` - First CMS index
- `swapLegs[].pricing.index2` - Second CMS index
- `swapLegs[].pricing.spread` - Spread between indices
- `swapLegs[].pricing.gearing` - Multiplier
- `swapLegs[].pricing.nakedOption` - "N" | "Y"
- `swapLegs[].pricing.digital` - Complex digital option structure
  ```json
  {
    "callPosition": "Long | Short",
    "isCallATMIncluded": false,
    "callStrikes": [array],
    "callPayoffs": [array],
    "putPosition": "Long | Short",
    "isPutATMIncluded": false,
    "putStrikes": [array],
    "putPayoffs": [array]
  }
  ```

**Example**: `digital-cms-spread-swap.json`


## Structural Patterns

### 1. Hierarchical Organization
All trades follow a consistent 4-level hierarchy:
```
Trade (top-level)
├── Metadata (tradeId, version, status, lastEvent)
├── General (parties, transaction info, common fields)
├── SwapDetails (swap-specific configuration)
└── SwapLegs (array of payment legs)
    ├── Leg metadata (type, parties, currency)
    ├── Pricing (rates, spreads, indices)
    └── Schedule (dates, periods, frequency)
```

### 2. Flexible Schema Pattern
The JSON structure demonstrates **schema flexibility**:
- Core fields are always present
- Optional fields appear based on swap subtype
- `x_nonCommonFields` array explicitly documents unique fields
- No rigid class hierarchy enforced

### 3. Pricing Variations by Rate Type

**Fixed Rate Pricing**:
```json
"pricing": {
  "interestRate": 2.35,
  "dayCountBasisIsda": "30/360"
}
```

**Floating Rate Pricing (IBOR)**:
```json
"pricing": {
  "ratesetRef": "EUR-EURIBOR-6M",
  "spreadBps": 0,
  "dayCountBasisIsda": "ACT/360",
  "style": "ibor"
}
```

**Overnight Rate Pricing**:
```json
"pricing": {
  "ratesetRef": "SOFR",
  "referenceTenor": "1D",
  "spreadBps": 8,
  "dayCountBasisIsda": "ACT/360",
  "accrualMethod": "Compounded",
  "rateCutOffDays": 2,
  "negativeRateMethod": "AllowNegative",
  "style": "overnight"
}
```


**Inflation Rate Pricing (CPI)**:
```json
"pricing": {
  "index": "UKRPI",
  "fixedRate": 2.00,
  "baseCpi": 210.0,
  "observationLag": "2M",
  "interpolated": false,
  "subtractInflationNotional": false
}
```

**Digital CMS Spread Pricing**:
```json
"pricing": {
  "index1": "EUR-CMS-10Y",
  "index2": "EUR-CMS-2Y",
  "spread": 10,
  "gearing": 8.0,
  "caps": [5.0],
  "floors": [1.0],
  "nakedOption": "N",
  "digital": { ... }
}
```

### 4. Schedule Patterns

**Standard Periodic Schedule (Original Format)**:
```json
"schedule": {
  "frequency": "semiannual",
  "startDate": "2026-01-17",
  "endDate": "2031-01-17",
  "periods": [
    { "start": "2026-01-17", "end": "2026-07-17", "ratesetDate": "2026-01-17" },
    ...
  ]
}
```

**Standard Periodic Schedule (ISO 8601 Format)**:
```json
"schedule": {
  "frequency": "P6M",
  "startDate": "2026-01-09",
  "endDate": "2031-01-09"
}
```

**Schedule with Payment/Roll Conventions**:
```json
"schedule": {
  "frequency": "P6M",
  "startDate": "2026-01-09",
  "endDate": "2031-01-09",
  "rollConvention": "Day1",
  "stubConvention": "ShortInitial",
  "paymentRelativeTo": "PeriodEnd",
  "paymentOffset": {
    "days": 2,
    "calendar": "USNY",
    "adjustmentConvention": "Following",
    "adjustmentCalendar": "USNY"
  }
}
```

**Amortizing Schedule** (with notional changes):
```json
"schedule": {
  "frequency": "annual",
  "startDate": "2026-06-17",
  "endDate": "2028-06-17",
  "periods": [
    { "start": "2026-06-17", "end": "2027-06-17", "notional": 100000000 },
    { "start": "2027-06-17", "end": "2028-06-17", "notional": 50000000 }
  ]
}
```

**Bullet Schedule** (single payment):
```json
"schedule": {
  "frequency": "bullet",
  "startDate": "2026-03-01",
  "endDate": "2028-03-01",
  "periods": [
    { "start": "2026-03-01", "end": "2028-03-01", "paymentDate": "2028-03-01" }
  ]
}
```


## Field Variability Analysis

### Always Present (100% of trades)
- `tradeId`, `tradeExtId`, `label`, `version`, `tradeType`, `status`
- `lastEvent.*` (all subfields)
- `general.common.*` (all subfields)
- `general.transactionInformation.*` (all subfields)
- `swapDetails.swapType`, `swapDetails.currency`
- `swapLegs[].legType`, `swapLegs[].currency`, `swapLegs[].rateType`, `swapLegs[].notional`
- `swapLegs[].schedule.frequency`, `swapLegs[].schedule.startDate`, `swapLegs[].schedule.endDate`

**Note**: `parties` location varies - sometimes in `general.parties`, sometimes at top level

### Frequently Present (50-99% of trades)
- `swapDetails.conventions.*` - Present in vanilla, forward-starting (~30%)
- `swapDetails.underlying` - Present in newer vanilla examples (~30%)
- `general.identifiers` / `general.sourceIdentifiers` - Present in some vanilla (~30%)
- `general.envelope` - Present in zero-coupon, CPI, YoY, digital CMS, EUR vanilla (~45%)
- `swapLegs[].pricing.dayCountBasisIsda` - Present in most (~90%)
- `swapLegs[].pricing.spreadBps` - Present in floating legs (~70%)

### Rarely Present (< 50% of trades)
- `swapDetails.oisConventions` - OIS only (~8%)
- `swapDetails.basis` - Basis swap only (~8%)
- `swapDetails.amortization` - Amortizing only (~8%)
- `swapDetails.notionalExchange` - Nonstandard only (~8%)
- `swapLegs[].pricing.digital` - Digital CMS only (~8%)
- `swapLegs[].pricing.caps/floors` - YoY, digital CMS (~15%)
- `general.regulatoryIdentifiers` - GBP vanilla only (~8%)
- `valuationSnapshot` - GBP vanilla only (~8%)

### Subtype-Specific Fields
Each swap subtype introduces 3-10 unique fields not present in other subtypes.


## Key Observations

### 1. JSON Composition Over Inheritance
The structure demonstrates **composition over inheritance**:
- No rigid class hierarchy
- Fields added/removed based on swap characteristics
- `x_nonCommonFields` explicitly documents variations
- Same field names can have different structures (e.g., `pricing` varies by `rateType`)

### 2. Field Naming Variations (CRITICAL)
**Multiple naming conventions exist for the same concepts**:

**Party References in Legs**:
- Original format: `payerPartyCode` / `receiverPartyCode`
- Newer format: `payer` / `receiver`

**Party Location**:
- Original format: `general.parties` (nested)
- Newer format: `parties` (top-level)

**Schedule Frequency**:
- Original format: String values ("annual", "semiannual", "quarterly")
- Newer format: ISO 8601 duration ("P1Y", "P6M", "P3M")

**Schedule Periods**:
- Original format: Explicit `periods` array with all dates
- Newer format: No `periods` array, dates calculated from frequency

**Identifiers**:
- Variation A: `general.identifiers` (scheme + id)
- Variation B: `general.sourceIdentifiers` (scheme + id)
- Variation C: `general.regulatoryIdentifiers` (uti + upi)

**Implication**: The API must handle **multiple field naming conventions** for the same logical data.

### 3. Metadata Richness
Every trade carries extensive metadata:
- **Lifecycle tracking**: `lastEvent` with full audit trail
- **Organizational context**: `general.envelope` with netting sets, portfolios
- **Transaction details**: Originator, price maker, execution venue
- **Party information**: Full LEI and role information
- **Regulatory data**: UTI/UPI identifiers (when applicable)
- **Valuation snapshots**: Optional pricing/NPV data

### 4. Flexible Pricing Models
The `pricing` object adapts to rate type:
- Fixed: Simple interest rate
- Floating IBOR: Reference rate + spread
- Overnight: Compounding method + rate cut-off
- Inflation: Index + observation lag + base CPI
- Digital: Complex option structures with strikes/payoffs

### 5. Schedule Flexibility
Schedules support multiple patterns:
- **Periodic**: Regular payment frequencies (string or ISO 8601)
- **Amortizing**: Notional changes per period
- **Bullet**: Single payment at maturity
- **Custom**: Explicit period definitions with dates
- **Advanced**: Roll conventions, stub conventions, payment offsets

### 6. Version Management
All trades include:
- `version` field at top level
- `lastEvent.version` tracking event sequence
- Support for amendments (see OIS example with version 2)

### 7. Status Lifecycle
Trades can have different statuses:
- **Confirmed**: Normal active trade (~92% of examples)
- **Abandoned**: Canceled trade (digital CMS example)
- Likely others: Pending, Settled, Terminated, etc.

### 8. Self-Documenting Structure
The `x_nonCommonFields` array serves as inline documentation:
- Lists fields unique to this trade instance
- Helps identify variations from standard templates
- Useful for validation and schema evolution

## Implications for API Design

### 1. Avoid Rigid Schemas
The API should:
- Accept flexible JSON structures
- Not enforce strict class hierarchies
- Allow optional fields based on swap subtype
- Support schema evolution without breaking changes

### 2. Handle Multiple Field Naming Conventions (CRITICAL)
The API must support **field name variations**:
- **Party references**: Accept both `payerPartyCode`/`receiverPartyCode` AND `payer`/`receiver`
- **Party location**: Check both `general.parties` AND top-level `parties`
- **Frequency formats**: Parse both string ("semiannual") AND ISO 8601 ("P6M")
- **Identifier locations**: Check `general.identifiers`, `general.sourceIdentifiers`, `general.regulatoryIdentifiers`
- **Periods**: Handle both explicit `periods` arrays AND calculated periods from frequency

**Recommendation**: Use **flexible accessor methods** that try multiple field paths:
```python
# Pseudocode example
def get_payer(leg):
    return leg.get('payer') or leg.get('payerPartyCode')

def get_parties(trade):
    return trade.get('parties') or trade.get('general', {}).get('parties', [])
```

### 3. Use JSON Composition Pattern
Recommended approach:
- Store trades as JSON documents
- Use dot notation for property access
- Avoid mapping to rigid object models
- Preserve original JSON structure
- Support multiple field naming conventions transparently

### 4. Template-Based Creation
For `/new` endpoint:
- Provide templates for each `swapType`
- Include common fields + subtype-specific fields
- Allow optional field population at creation time
- Generate unique IDs and metadata automatically
- **Support multiple template formats** (original vs newer conventions)

### 5. Flexible Validation
For `/validate` endpoint:
- Validate common fields across all trades
- Apply subtype-specific validation rules
- Check business logic (dates, consistency)
- Allow unknown fields (forward compatibility)
- **Accept multiple field naming conventions** without errors

### 6. Version Management Strategy
The API should:
- Track version numbers for all trades
- Maintain `lastEvent` history
- Support amendments with version increments
- Preserve audit trail with correlation IDs

## Field Statistics

### Top-Level Fields
- **Total unique top-level fields**: 9 (including optional `parties`)
- **Always present**: 7 (100%)
- **Optional**: 0

### general.* Fields
- **Total unique fields**: ~25
- **Always present**: ~15 (60%)
- **Optional**: ~10 (40%)
- **Subtype-specific**: `identifiers`, `envelope`

### swapDetails.* Fields
- **Total unique fields**: ~20
- **Always present**: 2 (`swapType`, `currency`)
- **Optional**: ~18 (90%)
- **Highly variable by subtype**

### swapLegs[].pricing.* Fields
- **Total unique fields**: ~30
- **Always present**: 0 (varies by `rateType`)
- **Rate-type specific**: 100%
- **Most complex variation point**

### swapLegs[].schedule.* Fields
- **Total unique fields**: ~8
- **Always present**: 4 (`frequency`, `startDate`, `endDate`, `periods`)
- **Optional**: 4 (50%)

## Recommendations for Trade Class Implementation

Based on this analysis, the Trade class should:

1. **Store raw JSON**: Preserve original structure without transformation
2. **Provide dot notation access**: `trade.general.common.book`
3. **Support dynamic fields**: Don't enforce rigid schema
4. **Validate flexibly**: Check required fields, allow optional fields
5. **Template generation**: Create subtype-specific templates
6. **Preserve metadata**: Maintain `lastEvent`, version, audit trail
7. **Handle arrays**: Support `swapLegs`, `parties`, `periods` arrays
8. **Allow extensions**: Support `x_nonCommonFields` and custom fields
9. **Handle field name variations**: Support multiple naming conventions transparently
10. **Flexible accessors**: Try multiple field paths when accessing data

## Vanilla IRS Variations Summary

The **4 vanilla IRS examples** reveal significant structural variations even within the same swap subtype:

| Feature | Original | EUR | GBP | USD |
|---------|----------|-----|-----|-----|
| Party refs in legs | `payerPartyCode` | `payer` | `payer` | `payer` |
| Party location | `general.parties` | Top-level | Top-level | Top-level |
| Frequency format | String | ISO 8601 | ISO 8601 | ISO 8601 |
| Periods array | Yes | No | No | No |
| Envelope | No | Yes | No | No |
| Regulatory IDs | No | No | Yes | No |
| Valuation snapshot | No | No | Yes | No |
| Payment offset | No | No | No | Yes |
| Fixing offset | No | No | No | Yes |

**Key Takeaway**: Even "vanilla" swaps show significant variation in field naming and structure. The API must be designed to handle these variations gracefully.

## Conclusion

The Interest Rate Swap JSON structure demonstrates a **flexible, composition-based design** that prioritizes:
- **Extensibility**: Easy to add new swap subtypes
- **Flexibility**: Fields vary based on business needs
- **Metadata richness**: Full audit trail and organizational context
- **Self-documentation**: `x_nonCommonFields` provides inline schema hints
- **Multiple conventions**: Support for different field naming patterns

**Critical Finding**: The addition of 3 new vanilla IRS examples reveals that **field naming conventions vary significantly** even within the same swap subtype. This has major implications for API design:

1. **Cannot assume single field naming convention**
2. **Must support multiple accessor patterns**
3. **Validation must be flexible about field names**
4. **Templates should support multiple formats**

This design is well-suited for a **JSON-first API** that avoids rigid object hierarchies and embraces schema flexibility while handling multiple field naming conventions transparently.
