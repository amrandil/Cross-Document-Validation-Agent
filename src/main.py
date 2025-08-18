"""Main FastAPI application for Multi-Document Fraud Detection Agent."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn

from .config import settings
from .api.routes import router as api_router
from .utils.logging_config import workflow_logger, log_step

# Initialize logging
log_step("start", message="Initializing Multi-Document Fraud Detection Agent")

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="LLM-powered agent for detecting fraud in customs declaration documents",
    docs_url="/docs",
    redoc_url="/redoc"
)

log_step("complete", message="FastAPI application created",
         title=settings.app_name, version=settings.app_version)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

log_step("complete", message="CORS middleware configured")

# Include API routes
app.include_router(api_router, prefix=settings.api_prefix)

log_step("complete", message="API routes included", prefix=settings.api_prefix)


@app.get("/")
async def root():
    """Root endpoint - redirect to API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }


def create_app() -> FastAPI:
    """Application factory."""
    return app


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
