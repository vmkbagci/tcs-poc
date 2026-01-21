"""Admin endpoints for store management (testing/development only)."""

import uuid
import random
from typing import Dict, List, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, status

from tcs_store.models import Context
from tcs_store.services.trade_service import TradeService
from pydantic import BaseModel, Field


router = APIRouter(prefix="/admin", tags=["admin"])


# Global variable to hold the service instance
_trade_service: TradeService | None = None


def set_trade_service(service: TradeService) -> None:
    """Set the trade service instance."""
    global _trade_service
    _trade_service = service


def get_trade_service() -> TradeService:
    """Dependency to get TradeService instance."""
    if _trade_service is None:
        raise NotImplementedError("TradeService dependency not configured")
    return _trade_service


class PurgeRequest(BaseModel):
    """Request to purge/clear the entire store."""
    
    context: Context = Field(..., description="Context metadata for lifecycle tracing")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "context": {
                        "user": "admin_user",
                        "agent": "admin_ui",
                        "action": "purge",
                        "intent": "test_cleanup"
                    }
                }
            ]
        }
    }


class SeedRequest(BaseModel):
    """Request to seed the store with example trades."""
    
    context: Context = Field(..., description="Context metadata for lifecycle tracing")
    count: int = Field(default=30, ge=1, le=100, description="Number of trades to generate (1-100)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "context": {
                        "user": "admin_user",
                        "agent": "admin_ui",
                        "action": "seed",
                        "intent": "test_data_setup"
                    },
                    "count": 30
                }
            ]
        }
    }


class PurgeResponse(BaseModel):
    """Response from purge operation."""
    message: str
    trades_deleted: int


class SeedResponse(BaseModel):
    """Response from seed operation."""
    message: str
    trades_created: int
    trade_ids: List[str]


def generate_ir_swap_trade(index: int) -> Dict[str, Any]:
    """
    Generate a random IR swap trade based on the template.
    
    Args:
        index: Index for generating unique IDs
        
    Returns:
        Trade data dictionary
    """
    # Generate random values
    notional = random.choice([1000, 5000, 10000, 25000, 50000, 100000])
    fixed_rate = round(random.uniform(2.5, 5.0), 2)
    margin = round(random.uniform(-0.5, 0.5), 2)
    
    # Random number of monthly periods (1-6 months)
    num_periods = random.choice([1, 2, 3, 4, 5, 6])
    
    # Generate dates - schedules are monthly
    base_date = datetime.now()
    start_date_dt = base_date + timedelta(days=random.randint(0, 30))
    start_date = start_date_dt.strftime("%Y-%m-%d")
    
    # End date spans all periods (monthly)
    end_date_dt = start_date_dt + timedelta(days=30 * num_periods)
    end_date = end_date_dt.strftime("%Y-%m-%d")
    
    # Random counterparties and books
    counterparties = ["02519916", "02519917", "02519918", "02519919", "02519920"]
    books = ["MEWEST01HS", "MEWEST02HS", "MEWEST03HS", "USEAST01HS", "USEAST02HS"]
    price_makers = ["kbagci", "vmenon", "nseeley"]
    
    trade_id = f"IR_SWAP_{uuid.uuid4().hex[:16].upper()}"
    
    # Generate schedule periods for both legs
    fixed_schedule = []
    floating_schedule = []
    
    for period_idx in range(num_periods):
        period_start = start_date_dt + timedelta(days=30 * period_idx)
        period_end = start_date_dt + timedelta(days=30 * (period_idx + 1))
        payment_date = period_end + timedelta(days=2)  # T+2 settlement
        
        # Fixed leg schedule
        fixed_schedule.append({
            "periodIndex": period_idx,
            "startDate": period_start.strftime("%Y-%m-%d"),
            "endDate": period_end.strftime("%Y-%m-%d"),
            "paymentDate": payment_date.strftime("%Y-%m-%d"),
            "rate": fixed_rate,
            "notional": -notional,
            "interest": round(-notional * fixed_rate / 100 * 30 / 360, 2)
        })
        
        # Floating leg schedule
        floating_schedule.append({
            "periodIndex": period_idx,
            "startDate": period_start.strftime("%Y-%m-%d"),
            "endDate": period_end.strftime("%Y-%m-%d"),
            "ratesetDate": period_end.strftime("%Y-%m-%d"),
            "paymentDate": payment_date.strftime("%Y-%m-%d"),
            "notional": notional,
            "margin": margin,
            "index": "SOFR",
            "tenor": "1D"
        })
    
    return {
        "id": trade_id,
        "data": {
            "general": {
                "tradeId": trade_id,
                "label": f"IR Swap {index + 1}",
                "transactionRoles": {
                    "marketer": None,
                    "transactionOriginator": None,
                    "priceMaker": random.choice(price_makers),
                    "transactionAcceptor": None,
                    "parameterGrantor": None
                },
                "executionDetails": {
                    "executionDateTime": datetime.now().isoformat() + "Z",
                    "bestExecutionApplicable": None,
                    "executionVenue": {
                        "executionVenue": None,
                        "venueTransactionID": None,
                        "executionBroker": None,
                        "executionBrokeragePayer": "wePay",
                        "executionVenueMIC": None,
                        "executionVenueType": "OffFacility"
                    },
                    "clearingVenue": None,
                    "reportTrackingNumber": None,
                    "omsOrderID": None,
                    "isOffMarketPrice": False,
                    "clientInstructionTime": None
                },
                "packageTradeDetails": {
                    "isPackageTrade": False,
                    "packageIdentifier": None,
                    "packagePriceOrSpread": None,
                    "packageType": None,
                    "packagePrice": None,
                    "packagePriceCcy": None,
                    "priceNotation": None,
                    "useTradeIdAsPackageId": True
                },
                "blockAllocationDetails": None
            },
            "common": {
                "book": random.choice(books),
                "accountReference": None,
                "tradeDate": start_date,
                "counterparty": random.choice(counterparties),
                "novatedToCounterparty": None,
                "counterpartyAccountReference": None,
                "inputDate": start_date,
                "orderTime": None,
                "comment": f"Auto-generated IR swap trade {index + 1} with {num_periods} monthly periods",
                "initialMargin": None,
                "backoutBook": None,
                "tradingStrategy": None,
                "ddeEligible": "No",
                "backoutTradingStrategy": None,
                "externalReference": None,
                "internalReference": None,
                "initialMarginDeliveryDate": None,
                "initialMarginDescription": None,
                "structureDetails": None,
                "backoutEntity": None,
                "salesGroup": None,
                "includeFeeEngine": {
                    "allLegs": False,
                    "nearLeg": False,
                    "farLeg": False,
                    "none": True
                },
                "acsLinkType": None,
                "regionOrAccount": None,
                "originatingSystem": None,
                "stp": "No",
                "sourceSystem": None,
                "cashflowHedgeNotification": False,
                "IRDAdvisory": False,
                "isCustomBasket": None,
                "events": [],
                "fees": [],
                "cvr": None,
                "rightToBreakDetails": None,
                "capitalSharing": [],
                "tagMap": [],
                "tradeIdentifiers": [],
                "ISDADefinition": "ISDA2021"
            },
            "swapDetails": {
                "underlying": "USD",
                "settlementType": "physical",
                "swapType": "irsOis",
                "isCleared": False,
                "markitSingleSided": False,
                "principalExchange": "firstLastLegs",
                "isIsdaFallback": False
            },
            "swapLegs": [
                {
                    "legIndex": 0,
                    "direction": "pay",
                    "currency": "USD",
                    "rateType": "fixed",
                    "notional": notional,
                    "scheduleType": "constant",
                    "interestRate": fixed_rate,
                    "ratesetRef": None,
                    "referenceTenor": None,
                    "margin": "marginNone",
                    "ratesetOffset": None,
                    "paymentOffset": None,
                    "formula": "ARR",
                    "dayCountBasis": "ACT/360",
                    "observationMethod": "notApplicable",
                    "averagingMethod": "notApplicable",
                    "startDate": start_date,
                    "endDate": end_date,
                    "isAdjusted": True,
                    "stubDate": None,
                    "stubType": "none",
                    "alignAtEom": "notEom",
                    "style": "notApplicable",
                    "rolloverDay": 16,
                    "settlementCurrency": "USD",
                    "settlementOffset": 2,
                    "paymentCalendars": ["NY"],
                    "rollDateConvention": "MFBD",
                    "schedule": fixed_schedule
                },
                {
                    "legIndex": 1,
                    "direction": "receive",
                    "currency": "USD",
                    "rateType": "floating",
                    "notional": notional,
                    "scheduleType": "constant",
                    "ratesetRef": "SOFR",
                    "referenceTenor": "1D",
                    "margin": margin,
                    "formula": "OIS",
                    "dayCountBasis": "ACT/360",
                    "observationMethod": "plain",
                    "averagingMethod": "compound",
                    "startDate": start_date,
                    "endDate": end_date,
                    "isAdjusted": True,
                    "stubType": "none",
                    "style": "floating-average-daily",
                    "rolloverDay": 16,
                    "settlementCurrency": "USD",
                    "settlementOffset": 2,
                    "paymentCalendars": ["NY"],
                    "rollDateConvention": "MFBD",
                    "schedule": floating_schedule
                }
            ]
        }
    }


@router.post(
    "/purge",
    status_code=status.HTTP_200_OK,
    response_model=PurgeResponse,
    summary="Purge/clear the entire store (DANGEROUS - Testing only)",
    description="""
    **⚠️ DANGEROUS OPERATION - USE WITH CAUTION ⚠️**
    
    Purge/clear all trades from the store. This operation is **irreversible** and should only be used for:
    - Testing and development
    - QA environment cleanup
    - Integration test teardown
    
    **DO NOT USE IN PRODUCTION**
    
    **Context Metadata Required:**
    - `user`: Identifier of the person or service account
    - `agent`: Identifier of the application or service
    - `action`: Should be "purge" or "clear"
    - `intent`: The reason for purging (e.g., "test_cleanup", "qa_reset")
    
    **Behavior:**
    - Deletes all trades from the store
    - Clears the operation log
    - Returns count of deleted trades
    - Logs the purge operation with context metadata
    """,
    responses={
        200: {
            "description": "Store purged successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Store purged successfully",
                        "trades_deleted": 42
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
async def purge_store(
    request: PurgeRequest,
    service: TradeService = Depends(get_trade_service)
) -> PurgeResponse:
    """Purge/clear all trades from the store (DANGEROUS - Testing only)."""
    # Get count before purging
    all_trades = service._store.get_all()
    count = len(all_trades)
    
    # Clear the store
    service._store.clear()
    
    return PurgeResponse(
        message="Store purged successfully",
        trades_deleted=count
    )


@router.post(
    "/seed",
    status_code=status.HTTP_201_CREATED,
    response_model=SeedResponse,
    summary="Seed the store with example IR swap trades",
    description="""
    Seed the store with randomly generated IR swap trades for testing and development.
    
    **Context Metadata Required:**
    - `user`: Identifier of the person or service account
    - `agent`: Identifier of the application or service
    - `action`: Should be "seed" or "bulk_import"
    - `intent`: The reason for seeding (e.g., "test_data_setup", "demo_preparation")
    
    **Generated Trade Variations:**
    - Random notionals: 1,000 to 100,000
    - Random fixed rates: 2.5% to 5.0%
    - Random margins: -0.5% to 0.5%
    - Random durations: 1 to 36 months
    - Random counterparties, books, and traders
    - Unique trade IDs for each trade
    
    **Behavior:**
    - Generates specified number of IR swap trades (1-100)
    - Each trade is a variation of the standard IR swap template
    - All trades are saved with the provided context metadata
    - Returns list of created trade IDs
    
    **Use Cases:**
    - Setting up test data for UI development
    - Preparing demo environments
    - Integration testing with realistic data
    - Performance testing with multiple trades
    """,
    responses={
        201: {
            "description": "Trades seeded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Successfully seeded 10 IR swap trades",
                        "trades_created": 10,
                        "trade_ids": [
                            "IR_SWAP_A1B2C3D4E5F6G7H8",
                            "IR_SWAP_B2C3D4E5F6G7H8I9"
                        ]
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
async def seed_store(
    request: SeedRequest,
    service: TradeService = Depends(get_trade_service)
) -> SeedResponse:
    """Seed the store with example IR swap trades."""
    trade_ids = []
    
    for i in range(request.count):
        trade = generate_ir_swap_trade(i)
        trade_id = trade["id"]
        
        # Save the trade using the service
        service.save_new(trade, request.context)
        trade_ids.append(trade_id)
    
    return SeedResponse(
        message=f"Successfully seeded {request.count} IR swap trades",
        trades_created=request.count,
        trade_ids=trade_ids
    )
