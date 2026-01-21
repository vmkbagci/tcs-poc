"""Filter models for querying trades."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TradeFilter(BaseModel):
    """Filter for querying trades."""
    
    # Structured common filters
    id: Optional[str] = Field(None, description="Single trade ID")
    ids: Optional[List[str]] = Field(None, description="List of trade IDs")
    
    # Flexible JSON filter for any field
    # Supports operators: eq, ne, gt, gte, lt, lte, regex, in, nin
    # Example: {"data.trade_type": {"eq": "IR_SWAP"}}
    # Example: {"data.trade_date": {"gte": "2024-01-01", "lte": "2024-12-31"}}
    # Example: {"data.counterparty": {"regex": "^BANK.*"}}
    filter: Optional[Dict[str, Any]] = Field(
        None,
        description="Flexible JSON filter with nested field paths and operators"
    )
    
    # Pagination (for future use)
    limit: Optional[int] = Field(None, ge=1, description="Maximum number of results")
    offset: Optional[int] = Field(None, ge=0, description="Number of results to skip")
    
    model_config = {
        "extra": "allow",
        "json_schema_extra": {
            "examples": [
                {
                    "filter": {
                        "data.trade_type": {"eq": "IR_SWAP"},
                        "data.notional": {"gte": 1000000}
                    }
                },
                {
                    "ids": ["trade-123", "trade-456"]
                },
                {
                    "filter": {
                        "data.counterparty": {"regex": "^BANK.*"}
                    },
                    "limit": 10,
                    "offset": 0
                }
            ]
        }
    }
