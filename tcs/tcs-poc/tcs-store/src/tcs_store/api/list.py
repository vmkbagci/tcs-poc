"""List operation endpoints."""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status

from tcs_store.models import (
    ListRequest,
    CountRequest,
    CountResponse,
)
from tcs_store.services.trade_service import TradeService
from tcs_store.exceptions import (
    InvalidContextError,
    InvalidFilterError,
)


router = APIRouter(prefix="/list", tags=["list"])


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
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[Dict[str, Any]],
    summary="List trades matching filter criteria",
    description="""
    List trades that match the specified filter criteria (returns simplified list items).
    
    **Context Metadata:** NOT required for read operations
    
    **Filter Operators:**
    - `eq`: Equals
    - `ne`: Not equals
    - `gt`, `gte`, `lt`, `lte`: Comparison operators
    - `regex`: Regular expression matching
    - `in`: Value in list
    - `nin`: Value not in list
    
    **Behavior:**
    - Returns 200 OK with list of matching trade list items
    - Returns 422 Unprocessable Entity if filter is invalid
    - Empty filter returns all trades
    """,
    responses={
        200: {
            "description": "Trade list items retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                            "data": {
                                "trade_type": "IR_SWAP",
                                "counterparty": "BANK_A"
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
async def list_trades(
    request: ListRequest,
    service: TradeService = Depends(get_trade_service)
) -> List[Dict[str, Any]]:
    """List trades matching a filter."""
    # Let exceptions propagate to global exception handlers
    trades = service.list_by_filter(request.filter)
    return trades


@router.post(
    "/count",
    status_code=status.HTTP_200_OK,
    response_model=CountResponse,
    summary="Count trades matching filter criteria",
    description="""
    Count the number of trades that match the specified filter criteria without retrieving full data.
    
    **Context Metadata:** NOT required for read operations
    
    **Filter Operators:**
    - `eq`: Equals
    - `ne`: Not equals
    - `gt`, `gte`, `lt`, `lte`: Comparison operators
    - `regex`: Regular expression matching
    - `in`: Value in list
    - `nin`: Value not in list
    
    **Behavior:**
    - Returns 200 OK with count of matching trades
    - Returns 422 Unprocessable Entity if filter is invalid
    - Empty filter counts all trades
    - Returns 0 if no trades match
    """,
    responses={
        200: {
            "description": "Count retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "count": 42
                    }
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
async def count_trades(
    request: CountRequest,
    service: TradeService = Depends(get_trade_service)
) -> CountResponse:
    """Count trades matching a filter."""
    # Let exceptions propagate to global exception handlers
    count = service.count_by_filter(request.filter)
    return CountResponse(count=count)
