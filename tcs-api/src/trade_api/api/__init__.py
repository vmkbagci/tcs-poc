"""API package for FastAPI routes and endpoints."""

from fastapi import APIRouter
from trade_api.api import trades

# Create main router
router = APIRouter()

# Include sub-routers
router.include_router(trades.router, prefix="/trades", tags=["trades"])