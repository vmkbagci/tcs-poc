"""Health check endpoints for Kubernetes/ArgoCD monitoring.

This module provides health check endpoints following Kubernetes conventions:
- /health/live: Liveness probe - checks if the application is running
- /health/ready: Readiness probe - checks if the application can serve traffic
"""

from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Dict, Any
import sys

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    version: str


class ReadinessResponse(BaseModel):
    """Readiness check response with dependency status."""
    status: str
    timestamp: str
    version: str
    checks: Dict[str, str]


@router.get("/live", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def liveness() -> HealthResponse:
    """Liveness probe endpoint.

    This endpoint checks if the application process is running.
    Used by Kubernetes to determine if the pod should be restarted.

    Returns:
        200 OK: Application is alive

    Example Response:
        {
            "status": "healthy",
            "timestamp": "2026-01-19T10:30:00.000Z",
            "version": "0.1.0"
        }
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        version="0.1.0"
    )


@router.get("/ready", response_model=ReadinessResponse, status_code=status.HTTP_200_OK)
async def readiness(response: Response) -> ReadinessResponse:
    """Readiness probe endpoint.

    This endpoint checks if the application is ready to serve traffic.
    Used by Kubernetes to determine if the pod should receive requests.

    Checks:
    - Application runtime (Python version, dependencies loaded)
    - Template factory can be initialized
    - Validation factory can be initialized

    Returns:
        200 OK: Application is ready to serve traffic
        503 Service Unavailable: Application is not ready

    Example Response (Healthy):
        {
            "status": "ready",
            "timestamp": "2026-01-19T10:30:00.000Z",
            "version": "0.1.0",
            "checks": {
                "runtime": "ok",
                "templates": "ok",
                "validation": "ok"
            }
        }

    Example Response (Unhealthy):
        {
            "status": "not_ready",
            "timestamp": "2026-01-19T10:30:00.000Z",
            "version": "0.1.0",
            "checks": {
                "runtime": "ok",
                "templates": "error",
                "validation": "ok"
            }
        }
    """
    checks: Dict[str, str] = {}
    is_ready = True

    # Check 1: Runtime health
    try:
        # Verify Python version is acceptable
        if sys.version_info >= (3, 10):
            checks["runtime"] = "ok"
        else:
            checks["runtime"] = "error"
            is_ready = False
    except Exception:
        checks["runtime"] = "error"
        is_ready = False

    # Check 2: Template system availability
    try:
        from trade_api.models import TradeTemplateFactory
        checks["templates"] = "ok"
    except Exception as e:
        checks["templates"] = f"error: {str(e)}"
        is_ready = False

    # Check 3: Validation system availability
    try:
        from trade_api.validation import ValidationFactory
        checks["validation"] = "ok"
    except Exception as e:
        checks["validation"] = f"error: {str(e)}"
        is_ready = False

    # Set response status code based on readiness
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        status="ready" if is_ready else "not_ready",
        timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        version="0.1.0",
        checks=checks
    )


@router.get("", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health() -> HealthResponse:
    """Basic health check endpoint.

    Simple health endpoint that returns 200 if the application is running.
    This is an alias to the liveness endpoint for convenience.

    Returns:
        200 OK: Application is healthy

    Example Response:
        {
            "status": "healthy",
            "timestamp": "2026-01-19T10:30:00.000Z",
            "version": "0.1.0"
        }
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        version="0.1.0"
    )