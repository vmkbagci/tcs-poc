"""Save operation endpoints."""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status

from tcs_store.models import SaveNewRequest, SaveUpdateRequest, PartialUpdateRequest
from tcs_store.services.trade_service import TradeService
from tcs_store.exceptions import (
    TradeNotFoundError,
    TradeAlreadyExistsError,
    InvalidContextError,
)


router = APIRouter(prefix="/save", tags=["save"])


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
    "/new",
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any],
    summary="Save a new trade",
    description="""
    Save a new trade to the store with context metadata for lifecycle tracing.
    
    **Context Metadata Required:**
    - `user`: Identifier of the person or service account making the request
    - `agent`: Identifier of the application or service making the request
    - `action`: The operation being performed (e.g., "save_new")
    - `intent`: The business reason or workflow step (e.g., "new_trade_booking")
    
    **Behavior:**
    - Returns 201 Created with the saved trade data
    - Returns 409 Conflict if a trade with the same ID already exists
    - Returns 422 Unprocessable Entity if context is missing or invalid
    
    **Idempotency:** NOT idempotent - duplicate IDs will fail with 409
    """,
    responses={
        201: {
            "description": "Trade created successfully",
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
        409: {
            "description": "Trade already exists",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Trade already exists",
                        "detail": "Trade with ID a1b2c3d4... already exists"
                    }
                }
            }
        },
        422: {
            "description": "Validation error or missing context",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Invalid context",
                        "detail": "Context field 'user' is required"
                    }
                }
            }
        }
    }
)
async def save_new(
    request: SaveNewRequest,
    service: TradeService = Depends(get_trade_service)
) -> Dict[str, Any]:
    """Save a new trade with context metadata."""
    # Let exceptions propagate to global exception handlers
    trade = service.save_new(request.trade, request.context)
    return trade


@router.post(
    "/update",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
    summary="Update an existing trade (full replacement)",
    description="""
    Update an existing trade by completely replacing its data with context metadata for lifecycle tracing.
    
    **Context Metadata Required:**
    - `user`: Identifier of the person or service account making the request
    - `agent`: Identifier of the application or service making the request
    - `action`: The operation being performed (e.g., "update")
    - `intent`: The business reason or workflow step (e.g., "trade_correction")
    
    **Behavior:**
    - Returns 200 OK with the updated trade data
    - Returns 404 Not Found if the trade ID does not exist
    - Returns 422 Unprocessable Entity if context is missing or invalid
    
    **Idempotency:** NOT idempotent - requires trade to exist
    """,
    responses={
        200: {
            "description": "Trade updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                        "data": {
                            "trade_type": "IR_SWAP",
                            "counterparty": "BANK_B",
                            "notional": 2000000,
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
        },
        422: {
            "description": "Validation error or missing context",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Invalid context",
                        "detail": "Context field 'agent' is required"
                    }
                }
            }
        }
    }
)
async def save_update(
    request: SaveUpdateRequest,
    service: TradeService = Depends(get_trade_service)
) -> Dict[str, Any]:
    """Update an existing trade (full replacement) with context metadata."""
    # Let exceptions propagate to global exception handlers
    trade = service.save_update(request.trade, request.context)
    return trade


@router.post(
    "/partial",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Any],
    summary="Partially update a trade using deep merge",
    description="""
    Partially update a trade by merging updates onto existing data with context metadata for lifecycle tracing.
    
    **Deep Merge Behavior:**
    - Nested dictionaries are merged recursively
    - Lists are replaced entirely (not merged)
    - Primitives are replaced with new values
    - **Null handling:**
      - Object/Dict + null → Field is removed
      - Primitive + null → Field is set to null
    
    **Context Metadata Required:**
    - `user`: Identifier of the person or service account making the request
    - `agent`: Identifier of the application or service making the request
    - `action`: The operation being performed (e.g., "partial_update")
    - `intent`: The business reason or workflow step (e.g., "notional_adjustment")
    
    **Behavior:**
    - Returns 200 OK with the updated trade data
    - Returns 404 Not Found if the trade ID does not exist
    - Returns 422 Unprocessable Entity if context is missing or invalid
    
    **Idempotency:** NOT idempotent - requires trade to exist
    """,
    responses={
        200: {
            "description": "Trade partially updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                        "data": {
                            "trade_type": "IR_SWAP",
                            "counterparty": "BANK_A",
                            "notional": 1500000,
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
        },
        422: {
            "description": "Validation error or missing context",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Invalid context",
                        "detail": "Context field 'intent' is required"
                    }
                }
            }
        }
    }
)
async def save_partial(
    request: PartialUpdateRequest,
    service: TradeService = Depends(get_trade_service)
) -> Dict[str, Any]:
    """Partially update a trade using deep merge with context metadata."""
    # Let exceptions propagate to global exception handlers
    trade = service.save_partial(request.id, request.updates, request.context)
    return trade
