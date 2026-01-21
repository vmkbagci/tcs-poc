"""Load operation endpoints."""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status

from tcs_store.models import (
    LoadByIdRequest,
    LoadGroupRequest,
    LoadFilterRequest,
    LoadGroupResponse,
)
from tcs_store.services.trade_service import TradeService
from tcs_store.exceptions import (
    TradeNotFoundError,
    InvalidContextError,
    InvalidFilterError,
)


router = APIRouter(prefix="/load", tags=["load"])


# Global variable to hold the service instance
_trade_service: TradeService | None = None


def set_trade_service(service: TradeService) -> None:
    """Set the trade service instance."""
    global _trade_service
    _trade_service = service


def get_trade_service() -> TradeService:
    """
    Dependency to get TradeService instance.
    
    This will be overridden in main.py to provide the actual service instance.
    """
    if _trade_service is None:
        raise NotImplementedError("TradeService dependency not configured")
    return _trade_service


@router.post(
    "/id",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
    summary="Load a single trade by ID",
    description="""
    Load a single trade by its unique identifier.
    
    **Context Metadata:** NOT required for read operations
    
    **Behavior:**
    - Returns 200 OK with the complete trade data
    - Returns 404 Not Found if the trade ID does not exist
    """,
    responses={
        200: {
            "description": "Trade loaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                        "data": {
                            "trade_type": "IR_SWAP",
                            "counterparty": "BANK_A",
                            "notional": 1000000,
                            "trade_date": "2024-01-15"
                        }
                    }
                }
            }
        },
        404: {
            "description": "Trade not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Trade not found",
                        "detail": "Trade with ID a1b2c3d4... not found"
                    }
                }
            }
        }
    }
)
async def load_by_id(
    request: LoadByIdRequest,
    service: TradeService = Depends(get_trade_service)
) -> Dict[str, Any]:
    """Load a single trade by ID."""
    # Let exceptions propagate to global exception handlers
    trade = service.load_by_id(request.id)
    return trade


@router.post(
    "/group",
    status_code=status.HTTP_200_OK,
    response_model=LoadGroupResponse,
    summary="Load multiple trades by IDs",
    description="""
    Load multiple trades by their unique identifiers in a single request.
    
    **Context Metadata:** NOT required for read operations
    
    **Behavior:**
    - Returns 200 OK with found trades and a list of missing IDs
    - Missing IDs are tracked but do not cause errors
    - Returns empty trades list if all IDs are missing
    """,
    responses={
        200: {
            "description": "Trades loaded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "trades": [
                            {
                                "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                                "data": {
                                    "trade_type": "IR_SWAP",
                                    "counterparty": "BANK_A",
                                    "notional": 1000000
                                }
                            },
                            {
                                "id": "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6a7",
                                "data": {
                                    "trade_type": "FX_SWAP",
                                    "counterparty": "BANK_B",
                                    "notional": 2000000
                                }
                            }
                        ],
                        "missing_ids": ["c3d4e5f6g7h8i9j0k1l2m3n4o5p6a7b8"]
                    }
                }
            }
        }
    }
)
async def load_group(
    request: LoadGroupRequest,
    service: TradeService = Depends(get_trade_service)
) -> LoadGroupResponse:
    """Load multiple trades by IDs."""
    # Let exceptions propagate to global exception handlers
    trades, missing_ids = service.load_by_ids(request.ids)
    return LoadGroupResponse(trades=trades, missing_ids=missing_ids)


@router.post(
    "/filter",
    status_code=status.HTTP_200_OK,
    response_model=List[Dict[str, Any]],
    summary="Load trades matching filter criteria",
    description="""
    Load all trades that match the specified filter criteria.
    
    **Context Metadata:** NOT required for read operations
    
    **Filter Operators:**
    - `eq`: Equals
    - `ne`: Not equals
    - `gt`, `gte`, `lt`, `lte`: Comparison operators
    - `regex`: Regular expression matching
    - `in`: Value in list
    - `nin`: Value not in list
    
    **Filter Behavior:**
    - Multiple conditions use AND logic (all must match)
    - Supports nested field paths (e.g., `data.leg1.notional`)
    - Empty filter returns all trades
    - Returns empty list if no trades match
    
    **Behavior:**
    - Returns 200 OK with list of matching trades
    - Returns 422 Unprocessable Entity if filter is invalid
    """,
    responses={
        200: {
            "description": "Trades loaded successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                            "data": {
                                "trade_type": "IR_SWAP",
                                "counterparty": "BANK_A",
                                "notional": 1000000
                            }
                        }
                    ]
                }
            }
        },
        422: {
            "description": "Invalid filter",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Invalid filter",
                        "detail": "Invalid operator: 'invalid_op'"
                    }
                }
            }
        }
    }
)
async def load_filter(
    request: LoadFilterRequest,
    service: TradeService = Depends(get_trade_service)
) -> List[Dict[str, Any]]:
    """Load trades matching a filter."""
    # Let exceptions propagate to global exception handlers
    trades = service.load_by_filter(request.filter)
    return trades
