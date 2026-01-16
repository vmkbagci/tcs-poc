This document provides a systematic framework for transforming functional, Algebraic Data Type (ADT) formatted JSON (referred to as "polar" format) into a flattened, business-logic-ready structure. It is designed to be used by human operators or as a detailed instruction set for AI models to ensure consistency across various derivative trade types.
Functional JSON Flattening Protocol

1. Core Principle: Unwrapping the "Option" Pattern
The most frequent pattern in polar JSON is the Option type, which explicitly handles presence or absence.
Step 1.1: Resolve "nothing" to null. Any object structured as {"nothing": null} must be converted to a raw null value 1-3. This maintains the field as a business entity placeholder for the server while removing structural noise 4-6.
Step 1.2: Resolve "just" to the raw value. Any object structured as {"just": value} must be unwrapped. For example, {"just": false} becomes false 2, 7, 8 and {"just": 1000} becomes 1000 9, 10.

2. Simplification of Sum Types (Variants)
Sum types are used for enums and structural branches where only one key is active and mapped to null.
Step 2.1: Convert Variant Keys to Strings. If an object contains a single key mapped to null (e.g., {"fixed": null} or {"No": null}), promote the key name to a string value 11-13.
Step 2.2: Handle Deeply Nested Variants. For complex hierarchies like {"floating": {"average": {"daily": null}}}, collapse the path into a single descriptive string: "floating-average-daily" 14-16.

3. Consolidation of Versioned Tuples (v1/v2)
Functional structures often use v1 and v2 keys to represent pairs or versioned records.
Step 3.1: Promote Indexing. In trade legs or schedules, v1 typically represents an index. Rename v1 to a context-specific name like legIndex or periodIndex 10, 12, 17, 18.
Step 3.2: Merge Payload. Unnest the contents of v2 into the primary object, effectively removing the v2 wrapper 12, 19, 20.

4. Temporal Data Consolidation
Polar JSON frequently fragments temporal data into separate date and time components.
Step 4.1: Merge Date and Time. Combine objects like executionDateTime (which split year, month, day, and hours into separate keys) into a single ISO-8601/UTC formatted string (e.g., "2026-01-16T05:22:16.000Z") 1, 6, 21, 22.
Step 4.2: Normalize Audit Dates. Ensure that business dates (like tradeDate or inputDate) are represented consistently, stripping away any "expression" wrappers that are set to nothing 7, 23-25.

5. Collapsing Product-Specific Hierarchies
Each asset class (IR-Swap, Commodity, Index) has unique nested structures that must be flattened for readability.
Step 5.1: Schedule Consolidation. In cash flow schedules, merge commonSchedule and additionalFloatingSchedule into a single period object 26-29.
Step 5.2: Reference Data Promotion. Extract critical identifiers from deep within the pricing logic—such as a floatingRate index name or tenor—and promote them to the top level of the schedule period 29-32.
Step 5.3: Block Reorganization.
For IR-Swaps, flatten swapStreamDetails and pricingDetails directly into the leg object 12, 33, 34.
For Commodity Options, collapse the commodityPayoff and assetPricing hierarchies into a flat commodityDetails block 35-38.
For Index Swaps, promote the indexCode from the underlyingAsset block into the primary leg definition 39, 40.

6. Business Value Retention
While flattening, specific production-ready values must be prioritized over generic placeholders.
Populate Active Identifiers: Ensure system-generated values like tradeId, correlationId, and eventDescription are explicitly captured in the flattened output 21, 22, 41, 42.
Maintain Operational Constants: Retain specific flags like reval: true or interpolation: "na" that appear in post-save versions, as these are critical for valuation 26, 43-45.

AI Prompt Implementation Guidance
When applying these rules to a new JSON:
Identify the asset class to select the correct destination block (swapLegs, commodityDetails, or leg) 46, 47.
Iterate through every field, applying the Option (just/nothing) and Sum Type rules first.
Audit the schedule arrays to ensure all v1/v2 and common/additional wrappers are removed.
Validate that the resulting JSON structure remains a valid flat object with standard types (string, number, boolean, null, or flat array).

