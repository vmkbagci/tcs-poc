# Swap Deals JSON Analysis

## Overview
This folder contains four JSON files representing different types of financial swap deals. Each file demonstrates the structured data format used to represent complex financial instruments with comprehensive trade details, lifecycle tracking, and audit trails.

## File Descriptions
- `ir-swap.json` → Interest Rate Swap
- `oi-swap.json` → Overnight Index Swap  
- `basis-swap.json` → Basis Swap
- `xcur-swap.json` → Cross-Currency Swap

## Common Data Structure

All swap deals share a consistent JSON schema with the following key sections:

### Trade Identification
- `tradeId`: Unique identifier (format: SWAP-YYYYMMDD-TYPE-NNNN)
- `tradeType`: Specific swap type (InterestRateSwap, OvernightIndexSwap, etc.)
- `assetClass`: Asset classification (Rates, RatesFX)
- `version`: Version number for trade amendments

### Trade Metadata
- `tradeDate`: Trade execution date
- `intermediary`: Trading intermediary (e.g., "Macquarie Global")
- `counterparties`: PartyA and PartyB with IDs and roles

### Terms
- `clearing`: Clearing method (Bilateral)
- `effectiveDate`: Trade start date
- `maturityDate`: Trade end date
- `priceConvention`: Pricing convention (Par)

### Legs Structure
Each swap contains 1-2 legs with detailed specifications:
- `legId`: Leg identifier
- `payReceive`: Payment direction (Pay/Receive)
- `currency`: Currency code
- `notional`: Principal amount
- `legType`: Fixed or Floating
- Rate specifications (fixedRate, index, spread)
- Day count conventions
- Payment/reset frequencies
- Business calendars and conventions

### Lifecycle Tracking
- `status`: Current trade status
- `lifecycles`: Array of audit events with:
  - Version tracking
  - Correlation IDs
  - Timestamps
  - Event types (Create, Amend)
  - User attribution
  - Platform information
  - Descriptive comments

## Swap Type Specifics

### Interest Rate Swap (IRS)
- Fixed leg vs floating leg in same currency (USD)
- Fixed leg: 4.25% semi-annual payments
- Floating leg: SOFR + 8bps quarterly payments
- 5-year term, $10M notional

### Overnight Index Swap (OIS)
- Fixed leg vs compounded overnight rate
- Special fields: compounding method, lookback/lockout days
- Annual payment frequency
- Uses SOFR as overnight index

### Basis Swap
- Two floating rate legs in same currency
- SOFR vs Term SOFR 3M + 12bps
- Both legs quarterly reset/payment
- $50M notional, 3-year term

### Cross-Currency Swap (XCCY)
- Multi-currency floating rates (USD SOFR vs EUR ESTR)
- FX-specific fields: spot rate, FX pair, notional exchanges
- Different notionals reflecting FX rate (10M USD vs 9.2M EUR)
- Asset class: "RatesFX"

## Key Observations

1. **Consistent Schema**: All swaps follow the same high-level structure despite different complexities
2. **Audit Trail**: Comprehensive lifecycle tracking with user attribution and timestamps
3. **Versioning**: Support for trade amendments with version control
4. **Flexibility**: Schema accommodates various swap types through the "specific" section
5. **Business Logic**: Proper handling of business day conventions, calendars, and market practices
6. **Data Integrity**: Rich metadata for trade reconstruction and regulatory reporting

## Dynamic Elements
As noted in the documentation, IDs for users (executedBy), counterparties, and correlation IDs are randomly generated and should be dynamically assigned during trade creation/modification.

## Potential Use Cases
This data structure supports:
- Trade capture and booking systems
- Risk management and valuation
- Regulatory reporting
- Trade lifecycle management
- Portfolio analytics
- Audit and compliance tracking