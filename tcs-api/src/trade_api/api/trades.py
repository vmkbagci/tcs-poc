"""Trade API endpoints for new, save, and validate operations."""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime
import uuid
from pathlib import Path

from trade_api.models import TradeTemplateFactory, Trade

router = APIRouter()
_template_factory = None

def get_template_factory() -> TradeTemplateFactory:
    global _template_factory
    if _template_factory is None:
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent
        template_dir = project_root / "templates"
        _template_factory = TradeTemplateFactory(template_dir=str(template_dir), schema_version="v1")
    return _template_factory

class SaveTradeRequest(BaseModel):
    trade_data: Dict[str, Any]

class ValidateTradeRequest(BaseModel):
    trade_data: Dict[str, Any]

class TradeResponse(BaseModel):
    success: bool
    trade_data: Optional[Dict[str, Any]] = None
    errors: List[str] = []
    warnings: List[str] = []
    metadata: Optional[Dict[str, Any]] = None

@router.get("/new", response_model=TradeResponse)
async def create_new_trade(
    trade_type: str = Query(..., description="Trade type: 'ir-swap', 'commodity-option', 'index-swap'", example="ir-swap")
) -> TradeResponse:
    try:
        factory = get_template_factory()
        assembler = factory.create_assembler(trade_type=trade_type)
        trade_dict = assembler.assemble()
        
        date_str = datetime.now().strftime("%Y%m%d")
        type_code = trade_type.upper().replace("-", "")
        sequence = str(uuid.uuid4().int)[:4]
        trade_id = f"NEW-{date_str}-{type_code}-{sequence}"
        
        if "general" in trade_dict:
            trade_dict["general"]["tradeId"] = trade_id
        
        today = datetime.now().strftime("%Y-%m-%d")
        execution_datetime = datetime.now().isoformat() + "Z"
        
        if "common" in trade_dict:
            trade_dict["common"]["tradeDate"] = today
            trade_dict["common"]["inputDate"] = today
        
        if "general" in trade_dict and "executionDetails" in trade_dict["general"]:
            trade_dict["general"]["executionDetails"]["executionDateTime"] = execution_datetime
        
        trade = Trade(trade_dict)
        metadata = {"trade_id": trade_id, "trade_type": trade_type, "template_schema_version": "v1"}
        return TradeResponse(success=True, trade_data=trade.data, metadata=metadata)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating template: {str(e)}")

@router.post("/save", response_model=TradeResponse)
async def save_trade(request: SaveTradeRequest) -> TradeResponse:
    return TradeResponse(success=True, trade_data={"message": "Placeholder"}, warnings=["Placeholder"])

@router.post("/validate", response_model=TradeResponse)
async def validate_trade(request: ValidateTradeRequest) -> TradeResponse:
    return TradeResponse(success=True, trade_data={"message": "Placeholder"}, warnings=["Placeholder"])
