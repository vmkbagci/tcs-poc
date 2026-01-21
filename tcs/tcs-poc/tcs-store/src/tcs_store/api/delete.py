"""Delete operation endpoints."""

from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status

from tcs_store.models import DeleteByIdRequest, DeleteGroupRequest, DeleteGroupResponse
from tcs_store.services.trade_service import TradeService
from tcs_store.exceptions import InvalidContextError


router = APIRouter(prefix="/delete", tags=["delete"])


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
    response_model=Dict[str, str],
    summary="Delete a single trade by ID (idempotent)",
    description="""
    Delete a single trade by its unique identifier with context metadata for lifecycle tracing.
    
    **Context Metadata Required:**
    - `user`: Identifier of the person or service account making the request
    - `agent`: Identifier of the application or service making the request
    - `action`: The operation being performed (e.g., "delete")
    - `intent`: The business reason or workflow step (e.g., "trade_cancellation")
    
    **Behavior:**
    - Returns 200 OK with success confirmation
    - Returns 422 Unprocessable Entity if context is missing or invalid
    
    **Idempotency:** IDEMPOTENT - deleting a non-existent trade returns success without error
    """,
    responses={
        200: {
            "description": "Trade deleted successfully (or already deleted)",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Trade a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6 deleted successfully"
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
                        "detail": "Context field 'action' is required"
                    }
                }
            }
        }
    }
)
async def delete_by_id(
    request: DeleteByIdRequest,
    service: TradeService = Depends(get_trade_service)
) -> Dict[str, str]:
    """Delete a single trade by ID (idempotent) with context metadata."""
    # Let exceptions propagate to global exception handlers
    service.delete_by_id(request.id, request.context)
    return {"message": f"Trade {request.id} deleted successfully"}


@router.post(
    "/group",
    status_code=status.HTTP_200_OK,
    response_model=DeleteGroupResponse,
    summary="Delete multiple trades by IDs (idempotent)",
    description="""
    Delete multiple trades by their unique identifiers in a single request with context metadata for lifecycle tracing.
    
    **Context Metadata Required:**
    - `user`: Identifier of the person or service account making the request
    - `agent`: Identifier of the application or service making the request
    - `action`: The operation being performed (e.g., "bulk_delete")
    - `intent`: The business reason or workflow step (e.g., "portfolio_cleanup")
    
    **Behavior:**
    - Returns 200 OK with deleted count and list of missing IDs
    - Missing IDs are tracked but do not cause errors
    - Returns 422 Unprocessable Entity if context is missing or invalid
    
    **Idempotency:** IDEMPOTENT - missing IDs are tracked but don't cause errors
    """,
    responses={
        200: {
            "description": "Trades deleted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "deleted_count": 2,
                        "missing_ids": ["c3d4e5f6g7h8i9j0k1l2m3n4o5p6a7b8"]
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
async def delete_group(
    request: DeleteGroupRequest,
    service: TradeService = Depends(get_trade_service)
) -> DeleteGroupResponse:
    """Delete multiple trades by IDs (idempotent) with context metadata."""
    # Let exceptions propagate to global exception handlers
    deleted_count, missing_ids = service.delete_by_ids(request.ids, request.context)
    return DeleteGroupResponse(deleted_count=deleted_count, missing_ids=missing_ids)
