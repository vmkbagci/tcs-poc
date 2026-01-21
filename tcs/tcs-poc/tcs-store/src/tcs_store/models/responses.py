"""Response models for API endpoints."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LoadGroupResponse(BaseModel):
    """Response for loading multiple trades."""
    
    trades: List[Dict[str, Any]] = Field(..., description="List of trades found")
    missing_ids: List[str] = Field(..., description="List of trade IDs that were not found")


class DeleteGroupResponse(BaseModel):
    """Response for deleting multiple trades."""
    
    deleted_count: int = Field(..., ge=0, description="Number of trades deleted")
    missing_ids: List[str] = Field(..., description="List of trade IDs that were not found")


class CountResponse(BaseModel):
    """Response for counting trades."""
    
    count: int = Field(..., ge=0, description="Number of trades matching the filter")


class ErrorResponse(BaseModel):
    """Error response."""
    
    error: str = Field(..., description="Brief error message")
    detail: Optional[str] = Field(None, description="Detailed explanation")


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    version: str = Field(..., description="Service version")


class ReadinessResponse(BaseModel):
    """Readiness check response with dependency status."""
    
    status: str = Field(..., description="Readiness status")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    version: str = Field(..., description="Service version")
    checks: Dict[str, str] = Field(..., description="Dependency check results")
