"""Request models for API endpoints."""

from typing import Any, Dict, List
from pydantic import BaseModel, Field

from .context import Context
from .filter import TradeFilter


class SaveNewRequest(BaseModel):
    """Request to save a new trade."""
    
    context: Context = Field(..., description="Context metadata for lifecycle tracing")
    trade: Dict[str, Any] = Field(..., description="Trade data (must include 'id' field)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "context": {
                        "user": "trader_123",
                        "agent": "trading_platform",
                        "action": "save_new",
                        "intent": "new_trade_booking"
                    },
                    "trade": {
                        "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                        "data": {
                            "trade_type": "IR_SWAP",
                            "counterparty": "BANK_A",
                            "notional": 1000000
                        }
                    }
                }
            ]
        }
    }


class SaveUpdateRequest(BaseModel):
    """Request to update an existing trade."""
    
    context: Context = Field(..., description="Context metadata for lifecycle tracing")
    trade: Dict[str, Any] = Field(..., description="Trade data (must include 'id' field)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "context": {
                        "user": "trader_123",
                        "agent": "trading_platform",
                        "action": "save_update",
                        "intent": "trade_correction"
                    },
                    "trade": {
                        "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                        "data": {
                            "trade_type": "IR_SWAP",
                            "counterparty": "BANK_B",
                            "notional": 2000000
                        }
                    }
                }
            ]
        }
    }


class PartialUpdateRequest(BaseModel):
    """Request to partially update a trade."""
    
    context: Context = Field(..., description="Context metadata for lifecycle tracing")
    id: str = Field(..., min_length=1, description="Trade ID to update")
    updates: Dict[str, Any] = Field(..., description="Partial trade data to merge")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "context": {
                        "user": "trader_123",
                        "agent": "trading_platform",
                        "action": "save_partial",
                        "intent": "update_schedule"
                    },
                    "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                    "updates": {
                        "data": {
                            "leg1": {
                                "schedule": {"start_date": "2024-02-01"}
                            }
                        }
                    }
                }
            ]
        }
    }


class LoadByIdRequest(BaseModel):
    """Request to load a single trade by ID."""
    
    id: str = Field(..., min_length=1, description="Trade ID to load")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
                }
            ]
        }
    }


class LoadGroupRequest(BaseModel):
    """Request to load multiple trades by IDs."""
    
    ids: List[str] = Field(..., min_items=1, description="List of trade IDs to load")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "ids": [
                        "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                        "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6a7",
                        "c3d4e5f6g7h8i9j0k1l2m3n4o5p6a7b8"
                    ]
                }
            ]
        }
    }


class LoadFilterRequest(BaseModel):
    """Request to load trades by filter."""
    
    filter: TradeFilter = Field(default_factory=lambda: TradeFilter(), description="Filter criteria")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "filter": {
                        "data.trade_type": {"eq": "IR_SWAP"},
                        "data.notional": {"gte": 1000000}
                    }
                }
            ]
        }
    }


class ListRequest(BaseModel):
    """Request to list trades by filter."""
    
    filter: TradeFilter = Field(default_factory=lambda: TradeFilter(), description="Filter criteria")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "filter": {
                        "data.trade_type": {"eq": "IR_SWAP"}
                    }
                }
            ]
        }
    }


class CountRequest(BaseModel):
    """Request to count trades by filter."""
    
    filter: TradeFilter = Field(default_factory=lambda: TradeFilter(), description="Filter criteria")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "filter": {
                        "data.counterparty": {"regex": "^BANK.*"}
                    }
                }
            ]
        }
    }


class DeleteByIdRequest(BaseModel):
    """Request to delete a single trade by ID."""
    
    context: Context = Field(..., description="Context metadata for lifecycle tracing")
    id: str = Field(..., min_length=1, description="Trade ID to delete")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "context": {
                        "user": "trader_123",
                        "agent": "trading_platform",
                        "action": "delete",
                        "intent": "trade_cancellation"
                    },
                    "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
                }
            ]
        }
    }


class DeleteGroupRequest(BaseModel):
    """Request to delete multiple trades by IDs."""
    
    context: Context = Field(..., description="Context metadata for lifecycle tracing")
    ids: List[str] = Field(..., min_length=1, description="List of trade IDs to delete")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "context": {
                        "user": "trader_123",
                        "agent": "trading_platform",
                        "action": "delete_group",
                        "intent": "cleanup_cancelled_trades"
                    },
                    "ids": ["trade-123", "trade-456"]
                }
            ]
        }
    }
