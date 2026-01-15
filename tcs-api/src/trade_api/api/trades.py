"""Trade API endpoints."""

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
    """Get or create template factory singleton."""
    global _template_factory
    if _template_factory is None:
        # Get project root (tcs-api directory)
        # Current file: tcs-api/src/trade_api/api/trades.py
        # Need to go up 4 levels: api -> trade_api -> src -> tcs-api
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent
        template_dir = project_root / "templates"
        
        _template_factory = TradeTemplateFactory(
            template_dir=str(template_dir),
            schema_version="v1"
        )
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
    trade_type: str = Query(..., description="Trade type (irswap, xccy)", example="irswap"),
    trade_subtype: str = Query(..., description="Subtype (vanilla, ois, basis)", example="vanilla"),
    currency: str = Query("EUR", description="Currency", example="EUR"),
    leg_types: str = Query("fixed,floating-ibor", description="Leg types", example="fixed,floating-ibor")
) -> TradeResponse:
    """Create new trade template."""
    try:
        type_mapping = {"irswap": "irs", "irs": "irs", "xccy": "xccy"}
        internal_type = type_mapping.get(trade_type.lower())
        if not internal_type:
            raise ValueError(f"Unknown trade type: {trade_type}")
        
        factory = get_template_factory()
        leg_type_list = [lt.strip() for lt in leg_types.split(",")]
        leg_configs = [{"type": lt, "legType": "Pay" if i == 0 else "Receive"} for i, lt in enumerate(leg_type_list)]
        
        assembler = factory.create_assembler(trade_type=internal_type, subtype=trade_subtype, currency=currency, leg_configs=leg_configs)
        trade_dict = assembler.assemble()
        
        date_str = datetime.now().strftime("%Y%m%d")
        trade_id = f"SWAP-{date_str}-{trade_type.upper()}-{trade_subtype.upper()}-{str(uuid.uuid4().int)[:4]}"
        trade_dict["tradeId"] = trade_id
        
        if "general" in trade_dict and "common" in trade_dict["general"]:
            trade_dict["general"]["common"]["tradeDate"] = datetime.now().strftime("%Y-%m-%d")
        
        trade_dict["lastEvent"] = {
            "version": 1,
            "correlationId": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat() + "Z",
            "intent": "BOOK_NEW_TRADE",
            "eventType": "Create",
            "executedBy": "",
            "platform": "TRADE_API",
            "comment": f"New {trade_subtype} {trade_type} template"
        }
        
        trade = Trade(trade_dict)
        return TradeResponse(success=True, trade_data=trade.data, metadata={"trade_id": trade_id, "trade_type": trade_type, "trade_subtype": trade_subtype, "currency": currency, "leg_count": len(leg_configs)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save", response_model=TradeResponse)
async def save_trade(request: SaveTradeRequest) -> TradeResponse:
    return TradeResponse(success=True, trade_data={"message": "Placeholder"}, warnings=["Placeholder"])

@router.post("/validate", response_model=TradeResponse)
async def validate_trade(request: ValidateTradeRequest) -> TradeResponse:
    return TradeResponse(success=True, trade_data={"message": "Placeholder"}, warnings=["Placeholder"])
