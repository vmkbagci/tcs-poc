"""Trade API endpoints for new, save, and validate operations."""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from pathlib import Path

from trade_api.models import TradeTemplateFactory
from trade_api.validation import ValidationFactory
from trade_api.services import TradeService

router = APIRouter()
_template_factory = None
_validation_factory = None

def get_template_factory() -> TradeTemplateFactory:
    global _template_factory
    if _template_factory is None:
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent
        template_dir = project_root / "templates"
        _template_factory = TradeTemplateFactory(template_dir=str(template_dir), schema_version="v1")
    return _template_factory

def get_validation_factory() -> ValidationFactory:
    """Get singleton ValidationFactory instance (lazy initialization)."""
    global _validation_factory
    if _validation_factory is None:
        _validation_factory = ValidationFactory()
        # Registry is built on first pipeline creation (lazy)
    return _validation_factory

def get_trade_service(
    template_factory: TradeTemplateFactory = Depends(get_template_factory),
    validation_factory: ValidationFactory = Depends(get_validation_factory)
) -> TradeService:
    """Get TradeService instance with injected dependencies.

    Args:
        template_factory: Factory for creating trade templates
        validation_factory: Factory for creating validation pipelines

    Returns:
        TradeService instance
    """
    return TradeService(template_factory, validation_factory)

class MetadataRequest(BaseModel):
    """Optional metadata for tracking."""
    documentId: Optional[str] = Field(None, description="UUID v4 document identifier")
    correlationId: Optional[str] = Field(None, description="UUID v4 correlation identifier")

class SaveTradeRequest(BaseModel):
    trade_data: Dict[str, Any]
    user: str = Field(..., min_length=1, description="User ID or service account making the request")
    agent: str = Field(..., min_length=1, description="Application or service identifier")
    action: str = Field(..., min_length=1, description="Operation being performed")
    intent: str = Field(..., min_length=1, description="Business reason or workflow step")

class ValidateTradeRequest(BaseModel):
    trade_data: Dict[str, Any]
    metadata: Optional[MetadataRequest] = None

class TradeResponse(BaseModel):
    success: bool
    trade_data: Optional[Dict[str, Any]] = None
    errors: List[str] = []
    warnings: List[str] = []
    metadata: Optional[Dict[str, Any]] = None

@router.get("/new", response_model=TradeResponse)
async def create_new_trade(
    trade_type: str = Query(..., description="Trade type: 'ir-swap', 'commodity-option', 'index-swap'", examples=["ir-swap"]),
    service: TradeService = Depends(get_trade_service)
) -> TradeResponse:
    """Create a new trade from a template.

    Args:
        trade_type: The type of trade to create
        service: TradeService instance (injected)

    Returns:
        TradeResponse with trade data and metadata

    Raises:
        HTTPException: If trade creation fails
    """
    result = service.create_new_trade(trade_type)

    if not result.success:
        if result.errors and "Invalid configuration" in result.errors[0]:
            raise HTTPException(status_code=400, detail=result.errors[0])
        raise HTTPException(status_code=500, detail=result.errors[0] if result.errors else "Unknown error")

    return TradeResponse(
        success=result.success,
        trade_data=result.trade_data,
        metadata=result.metadata,
        errors=result.errors
    )

@router.post("/save", response_model=TradeResponse)
async def save_trade(
    request: SaveTradeRequest,
    service: TradeService = Depends(get_trade_service)
) -> TradeResponse:
    """Save a trade.

    Flow:
    1. Detect if trade is new (tradeId starts with 'NEW')
    2. Validate the trade data
    3. If validation fails, return errors/warnings
    4. If validation passes, call tcs-store /save/new endpoint with context
    5. Return success with trade data and metadata

    Args:
        request: Request containing trade data and context (user, agent, action, intent)
        service: TradeService instance (injected)

    Returns:
        TradeResponse with save results
    """
    # Create context from request
    context = {
        "user": request.user,
        "agent": request.agent,
        "action": request.action,
        "intent": request.intent
    }
    
    result = service.save_trade(request.trade_data, context)

    return TradeResponse(
        success=result.success,
        trade_data=result.trade_data,
        warnings=result.warnings,
        errors=result.errors,
        metadata=result.metadata
    )

@router.post("/validate", response_model=TradeResponse)
async def validate_trade(
    request: ValidateTradeRequest,
    service: TradeService = Depends(get_trade_service)
) -> TradeResponse:
    """Validate trade data using validation pipeline.

    Args:
        request: Request containing trade data to validate
        service: TradeService instance (injected)

    Returns:
        TradeResponse with validation results (no trade_data returned)
    """
    # Convert Pydantic metadata to dict
    metadata_dict = None
    if request.metadata:
        metadata_dict = {
            "documentId": request.metadata.documentId,
            "correlationId": request.metadata.correlationId
        }

    # Call service with metadata
    result = service.validate_trade(
        trade_data=request.trade_data,
        metadata=metadata_dict
    )

    return TradeResponse(
        success=result.success,
        trade_data=None,
        errors=result.errors,
        warnings=result.warnings,
        metadata=result.metadata
    )