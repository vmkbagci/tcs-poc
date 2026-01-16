# Trade Enrichment Pipeline Strategy

## Overview

The Trade Enrichment Pipeline is a composable system for injecting runtime values into trade templates. It mirrors the template assembly pattern, using a pipeline of enrichers that apply transformations in sequence.

**Key Principle**: Templates define structure, enrichers inject runtime values.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Trade Creation Flow                      │
└─────────────────────────────────────────────────────────────────┘

1. Template Assembly (Structure)
   ┌──────────────────┐
   │ Template Factory │ → Assembler → Base Trade Dict
   └──────────────────┘
                ↓
2. Runtime Enrichment (Values)
   ┌──────────────────┐
   │ Enricher Factory │ → Pipeline → Enriched Trade Dict
   └──────────────────┘
                ↓
3. Trade Object Creation
   ┌──────────────────┐
   │  Trade(dict)     │ → Final Trade
   └──────────────────┘
```

## Core Concepts

### Enricher
A single-purpose class that injects specific runtime values into a trade dictionary.

**Characteristics**:
- Inherits from `BaseEnricher`
- Implements `enrich(trade_dict, context)` method
- Modifies trade_dict in-place
- Returns trade_dict for chaining
- Stateless (no instance variables)

### Pipeline
An ordered sequence of enrichers executed in composition order.

**Characteristics**:
- Similar to `TradeAssembler` but for enrichment
- Executes enrichers sequentially
- Each enricher receives output of previous enricher
- Context passed to all enrichers

### Factory
Creates pipelines by composing core + trade-specific enrichers.

**Characteristics**:
- Mirrors `TradeTemplateFactory` pattern
- Loads core enrichers (all trades)
- Loads trade-specific enrichers (per type)
- Returns configured pipeline

### Context
Dictionary containing metadata for enrichment decisions.

**Standard Keys**:
- `trade_type`: Trade type identifier (e.g., "ir-swap")
- `operation`: Operation type ("new", "save", "validate")
- `user_data`: Optional user-provided values

## Component Structure

```
src/trade_api/models/
├── enrichers/
│   ├── base.py                    # BaseEnricher abstract class
│   ├── core/                      # Core enrichers (ALL trades)
│   │   ├── trade_id.py           # TradeIdEnricher
│   │   └── timestamps.py         # TimestampEnricher
│   └── trade_types/               # Trade-specific enrichers
│       ├── ir_swap.py            # IRSwapEnricher
│       ├── commodity_option.py   # CommodityOptionEnricher
│       └── index_swap.py         # IndexSwapEnricher
├── enricher_pipeline.py           # EnricherPipeline
└── enricher_factory.py            # TradeEnricherFactory
```

## Enricher Types

### Core Enrichers
Apply to **ALL** trade types, regardless of specifics.

**Examples**:
- `TradeIdEnricher`: Generates trade IDs
- `TimestampEnricher`: Sets date/time fields
- `DefaultValueEnricher`: Sets common defaults

**Location**: `enrichers/core/`

### Trade-Specific Enrichers
Apply only to specific trade types.

**Examples**:
- `IRSwapEnricher`: IR swap specific logic
- `CommodityOptionEnricher`: Commodity option specific logic
- `IndexSwapEnricher`: Index swap specific logic

**Location**: `enrichers/trade_types/`

## Composition Order

Enrichers are applied in this order:

```
1. Core Enrichers (in registration order)
   ├── TradeIdEnricher
   └── TimestampEnricher

2. Trade-Specific Enrichers (if registered)
   └── {TradeType}Enricher
```

**Rationale**: Core values (ID, timestamps) should be set before trade-specific logic that might depend on them.

## Implementation Details

### BaseEnricher

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseEnricher(ABC):
    """Base class for all trade enrichers."""
    
    @abstractmethod
    def enrich(self, trade_dict: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply enrichment to trade dictionary.
        
        Args:
            trade_dict: Trade dictionary to enrich (modified in-place)
            context: Enrichment context (trade_type, operation, user_data)
            
        Returns:
            Enriched trade dictionary (same object)
        """
        pass
    
    def _set_nested_value(self, data: Dict, path: str, value: Any):
        """Set value at nested path like 'general.tradeId'."""
        keys = path.split('.')
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
    
    def _get_nested_value(self, data: Dict, path: str, default=None):
        """Get value at nested path."""
        keys = path.split('.')
        current = data
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current
```

### EnricherPipeline

```python
from typing import Dict, Any, List
from .enrichers.base import BaseEnricher

class EnricherPipeline:
    """Executes enrichers in sequence."""
    
    def __init__(self, *enrichers: BaseEnricher):
        self.enrichers = list(enrichers)
    
    def enrich(self, trade_dict: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all enrichers in order."""
        for enricher in self.enrichers:
            trade_dict = enricher.enrich(trade_dict, context)
        return trade_dict
```

### TradeEnricherFactory

```python
class TradeEnricherFactory:
    """Factory for creating enricher pipelines."""
    
    TRADE_TYPE_ENRICHERS = {
        "ir-swap": IRSwapEnricher,
        "commodity-option": CommodityOptionEnricher,
        "index-swap": IndexSwapEnricher,
    }
    
    def create_pipeline(self, trade_type: str, operation: str = "new") -> EnricherPipeline:
        """Create enricher pipeline for trade type and operation."""
        enrichers = []
        enrichers.extend(self._get_core_enrichers(operation))
        enrichers.extend(self._get_trade_enrichers(trade_type, operation))
        return EnricherPipeline(*enrichers)
    
    def _get_core_enrichers(self, operation: str) -> List[BaseEnricher]:
        """Get core enrichers based on operation."""
        if operation == "new":
            return [TradeIdEnricher(), TimestampEnricher()]
        elif operation == "save":
            return [TimestampEnricher()]
        return []
    
    def _get_trade_enrichers(self, trade_type: str, operation: str) -> List[BaseEnricher]:
        """Get trade-specific enrichers."""
        enricher_class = self.TRADE_TYPE_ENRICHERS.get(trade_type)
        return [enricher_class()] if enricher_class else []
```

## Example: IR Swap Creation

### Step-by-Step Flow

#### 1. Template Assembly
```python
# Endpoint receives request
trade_type = "ir-swap"

# Factory creates assembler
template_factory = TradeTemplateFactory(template_dir="templates", schema_version="v1")
assembler = template_factory.create_assembler(trade_type="ir-swap")

# Assembler composes templates
trade_dict = assembler.assemble()
```

**Result**: Base trade structure with empty runtime fields
```json
{
  "general": {
    "tradeId": "",
    "executionDetails": {
      "executionDateTime": ""
    }
  },
  "common": {
    "tradeDate": "",
    "inputDate": ""
  },
  "swapDetails": { ... },
  "swapLegs": [ ... ]
}
```

#### 2. Enrichment Pipeline Creation
```python
# Factory creates pipeline
enricher_factory = TradeEnricherFactory()
pipeline = enricher_factory.create_pipeline(trade_type="ir-swap", operation="new")

# Pipeline contains:
# [TradeIdEnricher, TimestampEnricher, IRSwapEnricher]
```

#### 3. Context Preparation
```python
context = {
    "trade_type": "ir-swap",
    "operation": "new",
    "user_data": {}
}
```

#### 4. Enrichment Execution
```python
enriched_trade = pipeline.enrich(trade_dict, context)
```

**Enricher 1: TradeIdEnricher**
```python
# Generates: NEW-20260116-IRSWAP-1234
trade_dict["general"]["tradeId"] = "NEW-20260116-IRSWAP-1234"
```

**Enricher 2: TimestampEnricher**
```python
# Sets current date/time
trade_dict["common"]["tradeDate"] = "2026-01-16"
trade_dict["common"]["inputDate"] = "2026-01-16"
trade_dict["general"]["executionDetails"]["executionDateTime"] = "2026-01-16T10:30:00.000Z"
```

**Enricher 3: IRSwapEnricher**
```python
# IR-swap specific logic (example)
for idx, leg in enumerate(trade_dict["swapLegs"]):
    if leg.get("legIndex") is None:
        leg["legIndex"] = idx
```

#### 5. Final Result
```json
{
  "general": {
    "tradeId": "NEW-20260116-IRSWAP-1234",
    "executionDetails": {
      "executionDateTime": "2026-01-16T10:30:00.000Z"
    }
  },
  "common": {
    "tradeDate": "2026-01-16",
    "inputDate": "2026-01-16"
  },
  "swapDetails": { ... },
  "swapLegs": [
    { "legIndex": 0, ... },
    { "legIndex": 1, ... }
  ]
}
```

### Complete Endpoint Code

```python
@router.get("/new", response_model=TradeResponse)
async def create_new_trade(
    trade_type: str = Query(..., example="ir-swap")
) -> TradeResponse:
    """Create new trade with template assembly + enrichment."""
    try:
        # 1. Assemble template structure
        template_factory = get_template_factory()
        assembler = template_factory.create_assembler(trade_type=trade_type)
        trade_dict = assembler.assemble()
        
        # 2. Enrich with runtime values
        enricher_factory = get_enricher_factory()
        pipeline = enricher_factory.create_pipeline(
            trade_type=trade_type, 
            operation="new"
        )
        
        context = {
            "trade_type": trade_type,
            "operation": "new",
            "user_data": {}
        }
        
        enriched_trade = pipeline.enrich(trade_dict, context)
        
        # 3. Create Trade object
        trade = Trade(enriched_trade)
        
        # 4. Build response metadata
        trade_id = trade.data.get("general", {}).get("tradeId", "")
        metadata = {
            "trade_id": trade_id,
            "trade_type": trade_type,
            "template_schema_version": "v1"
        }
        
        return TradeResponse(
            success=True, 
            trade_data=trade.data, 
            metadata=metadata
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Core Enricher Examples

### TradeIdEnricher

```python
from datetime import datetime
import uuid
from ..base import BaseEnricher

class TradeIdEnricher(BaseEnricher):
    """Generates and sets trade ID for new trades.
    
    Format: NEW-{YYYYMMDD}-{TRADETYPE}-{SEQUENCE}
    Example: NEW-20260116-IRSWAP-1234
    """
    
    def enrich(self, trade_dict, context):
        operation = context.get("operation", "new")
        
        if operation == "new":
            trade_type = context.get("trade_type", "UNKNOWN")
            date_str = datetime.now().strftime("%Y%m%d")
            type_code = trade_type.upper().replace("-", "")
            sequence = str(uuid.uuid4().int)[:4]
            
            trade_id = f"NEW-{date_str}-{type_code}-{sequence}"
            self._set_nested_value(trade_dict, "general.tradeId", trade_id)
        
        return trade_dict
```

### TimestampEnricher

```python
from datetime import datetime
from ..base import BaseEnricher

class TimestampEnricher(BaseEnricher):
    """Sets all timestamp fields with current date/time.
    
    Fields set:
    - common.tradeDate (YYYY-MM-DD)
    - common.inputDate (YYYY-MM-DD)
    - general.executionDetails.executionDateTime (ISO 8601)
    """
    
    def enrich(self, trade_dict, context):
        operation = context.get("operation", "new")
        
        if operation in ["new", "save"]:
            today = datetime.now().strftime("%Y-%m-%d")
            execution_datetime = datetime.now().isoformat() + "Z"
            
            # Set common timestamps
            self._set_nested_value(trade_dict, "common.tradeDate", today)
            self._set_nested_value(trade_dict, "common.inputDate", today)
            
            # Set execution timestamp
            self._set_nested_value(
                trade_dict,
                "general.executionDetails.executionDateTime",
                execution_datetime
            )
        
        return trade_dict
```

## Trade-Specific Enricher Example

### IRSwapEnricher

```python
from ..base import BaseEnricher

class IRSwapEnricher(BaseEnricher):
    """IR Swap specific enrichments.
    
    Responsibilities:
    - Set leg indices if missing
    - Apply IR-swap specific defaults
    - Validate IR-swap specific constraints
    """
    
    def enrich(self, trade_dict, context):
        operation = context.get("operation", "new")
        
        if operation == "new":
            self._set_leg_indices(trade_dict)
            self._apply_ir_swap_defaults(trade_dict)
        
        return trade_dict
    
    def _set_leg_indices(self, trade_dict):
        """Ensure all swap legs have sequential indices."""
        if "swapLegs" in trade_dict:
            for idx, leg in enumerate(trade_dict["swapLegs"]):
                if "legIndex" not in leg or leg["legIndex"] is None:
                    leg["legIndex"] = idx
    
    def _apply_ir_swap_defaults(self, trade_dict):
        """Apply IR-swap specific defaults."""
        # Example: Set default settlement conventions
        # This is where trade-specific business logic goes
        pass
```

## Operation-Specific Behavior

### "new" Operation
Creates a brand new trade from template.

**Enrichers Applied**:
- `TradeIdEnricher`: Generate NEW-* ID
- `TimestampEnricher`: Set all timestamps
- Trade-specific enricher: Apply defaults

**Use Case**: `/new` endpoint

### "save" Operation
Updates an existing trade being saved.

**Enrichers Applied**:
- `TimestampEnricher`: Update timestamps only
- Trade-specific enricher: Apply validation/updates

**Use Case**: `/save` endpoint

**Note**: TradeIdEnricher NOT applied (preserve existing ID)

### "validate" Operation
Validates trade without modification.

**Enrichers Applied**:
- None (validation only, no enrichment)

**Use Case**: `/validate` endpoint

## Extension Points

### Adding New Core Enricher

1. Create enricher class in `enrichers/core/`
2. Inherit from `BaseEnricher`
3. Implement `enrich()` method
4. Register in `TradeEnricherFactory._get_core_enrichers()`

**Example**: Adding a `UserContextEnricher`
```python
# enrichers/core/user_context.py
class UserContextEnricher(BaseEnricher):
    def enrich(self, trade_dict, context):
        user_data = context.get("user_data", {})
        if "trader" in user_data:
            self._set_nested_value(trade_dict, "general.trader", user_data["trader"])
        return trade_dict

# enricher_factory.py
def _get_core_enrichers(self, operation):
    if operation == "new":
        return [
            TradeIdEnricher(),
            TimestampEnricher(),
            UserContextEnricher(),  # NEW
        ]
```

### Adding New Trade-Specific Enricher

1. Create enricher class in `enrichers/trade_types/`
2. Inherit from `BaseEnricher`
3. Implement `enrich()` method
4. Register in `TradeEnricherFactory.TRADE_TYPE_ENRICHERS`

**Example**: Adding `FXSwapEnricher`
```python
# enrichers/trade_types/fx_swap.py
class FXSwapEnricher(BaseEnricher):
    def enrich(self, trade_dict, context):
        # FX swap specific logic
        return trade_dict

# enricher_factory.py
TRADE_TYPE_ENRICHERS = {
    "ir-swap": IRSwapEnricher,
    "commodity-option": CommodityOptionEnricher,
    "index-swap": IndexSwapEnricher,
    "fx-swap": FXSwapEnricher,  # NEW
}
```

### Dynamic Registration

```python
# Register custom enricher at runtime
enricher_factory = TradeEnricherFactory()
enricher_factory.register_enricher("custom-trade", CustomEnricher)

# Now available for use
pipeline = enricher_factory.create_pipeline(trade_type="custom-trade", operation="new")
```

## Testing Strategy

### Unit Testing Enrichers

```python
def test_trade_id_enricher():
    enricher = TradeIdEnricher()
    trade_dict = {"general": {}}
    context = {"trade_type": "ir-swap", "operation": "new"}
    
    result = enricher.enrich(trade_dict, context)
    
    assert "tradeId" in result["general"]
    assert result["general"]["tradeId"].startswith("NEW-")
    assert "IRSWAP" in result["general"]["tradeId"]
```

### Integration Testing Pipeline

```python
def test_ir_swap_pipeline():
    factory = TradeEnricherFactory()
    pipeline = factory.create_pipeline(trade_type="ir-swap", operation="new")
    
    trade_dict = {
        "general": {},
        "common": {},
        "swapLegs": [{"legIndex": None}, {"legIndex": None}]
    }
    
    context = {"trade_type": "ir-swap", "operation": "new"}
    result = pipeline.enrich(trade_dict, context)
    
    # Verify all enrichments applied
    assert result["general"]["tradeId"].startswith("NEW-")
    assert result["common"]["tradeDate"] != ""
    assert result["swapLegs"][0]["legIndex"] == 0
    assert result["swapLegs"][1]["legIndex"] == 1
```

### End-to-End Testing

```python
def test_create_new_ir_swap_endpoint():
    response = client.get("/api/v1/trades/new?trade_type=ir-swap")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify structure
    assert "trade_data" in data
    assert "metadata" in data
    
    # Verify enrichments
    trade = data["trade_data"]
    assert trade["general"]["tradeId"].startswith("NEW-")
    assert trade["common"]["tradeDate"] != ""
    assert len(trade["swapLegs"]) == 2
```

## Best Practices

### 1. Keep Enrichers Focused
Each enricher should have a single, clear responsibility.

**Good**:
```python
class TradeIdEnricher(BaseEnricher):
    """Only generates and sets trade ID."""
```

**Bad**:
```python
class TradeSetupEnricher(BaseEnricher):
    """Sets ID, timestamps, defaults, and validates."""
```

### 2. Use Context for Decisions
Don't hard-code behavior; use context to make decisions.

**Good**:
```python
def enrich(self, trade_dict, context):
    operation = context.get("operation")
    if operation == "new":
        # Generate new ID
```

**Bad**:
```python
def enrich(self, trade_dict, context):
    # Always generate new ID
```

### 3. Fail Gracefully
Handle missing fields without crashing.

**Good**:
```python
if "swapLegs" in trade_dict:
    for leg in trade_dict["swapLegs"]:
        # Process leg
```

**Bad**:
```python
for leg in trade_dict["swapLegs"]:  # KeyError if missing
    # Process leg
```

### 4. Document Field Paths
Clearly document which fields each enricher modifies.

```python
class TimestampEnricher(BaseEnricher):
    """Sets timestamp fields.
    
    Fields modified:
    - common.tradeDate
    - common.inputDate
    - general.executionDetails.executionDateTime
    """
```

### 5. Make Enrichers Stateless
Don't store state in enricher instances.

**Good**:
```python
class TradeIdEnricher(BaseEnricher):
    def enrich(self, trade_dict, context):
        # Use context, not instance variables
```

**Bad**:
```python
class TradeIdEnricher(BaseEnricher):
    def __init__(self):
        self.last_id = None  # BAD: stateful
```

## Comparison: Templates vs Enrichers

| Aspect | Templates | Enrichers |
|--------|-----------|-----------|
| **Purpose** | Define structure | Inject runtime values |
| **Format** | JSON files | Python classes |
| **Composition** | File merge | Pipeline execution |
| **When Applied** | Assembly phase | Enrichment phase |
| **Extensibility** | Add JSON files | Add Python classes |
| **Examples** | Field definitions, defaults | IDs, timestamps, calculations |

## Migration Path

### Current State (Before)
```python
# Endpoint does everything
@router.get("/new")
async def create_new_trade(trade_type: str):
    trade_dict = assembler.assemble()
    
    # Hard-coded enrichment
    trade_dict["general"]["tradeId"] = generate_id()
    trade_dict["common"]["tradeDate"] = get_today()
    # ... more hard-coded logic
    
    return trade_dict
```

### Target State (After)
```python
# Endpoint orchestrates
@router.get("/new")
async def create_new_trade(trade_type: str):
    # 1. Assemble structure
    trade_dict = template_factory.create_assembler(trade_type).assemble()
    
    # 2. Enrich with values
    pipeline = enricher_factory.create_pipeline(trade_type, "new")
    enriched = pipeline.enrich(trade_dict, context)
    
    return enriched
```

## Summary

The Enrichment Pipeline provides:

- **Separation of Concerns**: Templates handle structure, enrichers handle values
- **Composability**: Core + trade-specific enrichers
- **Extensibility**: Add enrichers without changing endpoints
- **Testability**: Each component independently testable
- **Consistency**: Same pattern as template assembly
- **Flexibility**: Different enrichers per operation

This architecture scales cleanly as new trade types and enrichment requirements are added.
