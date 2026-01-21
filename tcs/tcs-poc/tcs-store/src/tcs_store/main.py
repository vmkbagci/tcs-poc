"""Main FastAPI application for TCS Store."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from tcs_store.storage.in_memory_store import InMemoryStore
from tcs_store.services.trade_service import TradeService
from tcs_store.api import save, load, list as list_api, delete, health, admin
from tcs_store.exceptions import (
    TradeNotFoundError,
    TradeAlreadyExistsError,
    InvalidFilterError,
    InvalidContextError,
)

# Create singleton instances
store = InMemoryStore()
trade_service = TradeService(store)

app = FastAPI(
    title="TCS Store API",
    description="""
    In-memory trade storage API with lifecycle tracing through context metadata.
    
    ## Overview
    
    The TCS Store provides RESTful endpoints for managing trade data in memory with comprehensive 
    lifecycle tracing. All mutating operations (save, delete) require context metadata for audit trails.
    
    ## Context Metadata
    
    Context metadata enables lifecycle tracing and audit trails. Required for all save and delete operations:
    
    - **user**: Identifier of the person or service account making the request
    - **agent**: Identifier of the application or service making the request
    - **action**: The operation being performed (e.g., "save_new", "update", "delete")
    - **intent**: The business reason or workflow step (e.g., "new_trade_booking", "trade_correction")
    
    **Context is NOT required for read operations** (load, list, count) or health checks.
    
    ## Filter Syntax
    
    Filters support various operators for querying trades:
    
    - **eq**: Equals
    - **ne**: Not equals
    - **gt**, **gte**, **lt**, **lte**: Comparison operators
    - **regex**: Regular expression matching
    - **in**: Value in list
    - **nin**: Value not in list
    
    Multiple conditions use AND logic. Supports nested field paths (e.g., `data.leg1.notional`).
    
    ## Deep Merge Behavior
    
    Partial updates use deep merge with smart null handling:
    
    - **Nested dictionaries**: Merged recursively
    - **Lists**: Replaced entirely (not merged)
    - **Primitives**: Replaced with new value
    - **Null handling**:
      - Object/Dict + null → Field is removed
      - Primitive + null → Field is set to null
    
    ## Idempotency
    
    - **DELETE operations**: Idempotent (always return 200)
    - **UPDATE operations**: NOT idempotent (require trade to exist, return 404 if not)
    - **SAVE operations**: NOT idempotent (duplicate IDs fail with 409)
    """,
    version="0.1.0",
    contact={
        "name": "TCS Store API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "Proprietary",
    },
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set the trade service for dependency injection
save.set_trade_service(trade_service)
load.set_trade_service(trade_service)
list_api.set_trade_service(trade_service)
delete.set_trade_service(trade_service)
admin.set_trade_service(trade_service)

# Register routers
app.include_router(save.router)
app.include_router(load.router)
app.include_router(list_api.router)
app.include_router(delete.router)
app.include_router(health.router)
app.include_router(admin.router)


# Exception handlers
@app.exception_handler(TradeNotFoundError)
async def trade_not_found_handler(request: Request, exc: TradeNotFoundError):
    """Handle TradeNotFoundError with 404 status."""
    return JSONResponse(
        status_code=404,
        content={"error": "Trade not found", "detail": str(exc)}
    )


@app.exception_handler(TradeAlreadyExistsError)
async def trade_already_exists_handler(request: Request, exc: TradeAlreadyExistsError):
    """Handle TradeAlreadyExistsError with 409 status."""
    return JSONResponse(
        status_code=409,
        content={"error": "Trade already exists", "detail": str(exc)}
    )


@app.exception_handler(InvalidFilterError)
async def invalid_filter_handler(request: Request, exc: InvalidFilterError):
    """Handle InvalidFilterError with 422 status."""
    return JSONResponse(
        status_code=422,
        content={"error": "Invalid filter", "detail": str(exc)}
    )


@app.exception_handler(InvalidContextError)
async def invalid_context_handler(request: Request, exc: InvalidContextError):
    """Handle InvalidContextError with 422 status."""
    return JSONResponse(
        status_code=422,
        content={"error": "Invalid context", "detail": str(exc)}
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle Pydantic ValidationError with 422 status."""
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "detail": str(exc)}
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError with 422 status."""
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "detail": str(exc)}
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions with 500 status."""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    pass


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    pass


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "TCS Store API", "version": "0.1.0"}
