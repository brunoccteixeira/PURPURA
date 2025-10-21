"""
PÚRPURA Climate OS — API Server
FastAPI application for climate risk assessment and IFRS S2 compliance
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import os

# Import routers
from .routers import documents, extraction, risk, compliance, health, metrics, ratelimit

# Import rate limiter
from backend.middleware.rate_limit import (
    limiter,
    custom_rate_limit_exceeded_handler,
    rate_limit_middleware
)

# Environment
API_VERSION = os.getenv("API_VERSION", "1.0.0")
ENV = os.getenv("ENV", "development")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"🟣 PÚRPURA API v{API_VERSION} starting ({ENV})...")
    # TODO: Initialize database connections
    # TODO: Load ML models
    # TODO: Connect to Trino
    yield
    # Shutdown
    print("🟣 PÚRPURA API shutting down...")
    # TODO: Close database connections


# Create FastAPI app
app = FastAPI(
    title="PÚRPURA Climate OS API",
    description="Climate risk assessment and IFRS S2 compliance platform",
    version=API_VERSION,
    lifespan=lifespan,
)

# Add rate limiter to app state
app.state.limiter = limiter

# Add rate limit exception handler
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limit middleware
app.middleware("http")(rate_limit_middleware)

# Include routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(metrics.router, prefix="/api/v1")
app.include_router(ratelimit.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(extraction.router, prefix="/api/v1/extraction", tags=["Extraction"])
app.include_router(risk.router, prefix="/api/v1/risk", tags=["Risk Assessment"])
app.include_router(compliance.router, prefix="/api/v1/compliance", tags=["Compliance"])


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "PÚRPURA Climate OS API",
        "version": API_VERSION,
        "environment": ENV,
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # TODO: Add actual health checks (DB, Trino, etc.)
    return {
        "status": "healthy",
        "version": API_VERSION,
        "services": {
            "api": "up",
            "database": "unknown",  # TODO
            "trino": "unknown",  # TODO
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if ENV == "development" else False,
    )
