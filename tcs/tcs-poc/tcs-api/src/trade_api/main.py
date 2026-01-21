"""Main application factory and FastAPI app configuration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from trade_api.config import get_settings
from trade_api.api import router
from trade_api.api.health import router as health_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Trade API",
        description="FastAPI-based system for processing financial swap deals",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Configure CORS to allow requests from any source
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
        allow_headers=["*"],  # Allow all headers
    )

    # Include health check routes (no prefix for standard k8s/ArgoCD paths)
    app.include_router(health_router)

    # Include API routes
    app.include_router(router, prefix="/api/v1")

    return app


# Create the app instance for uvicorn
app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "trade_api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )