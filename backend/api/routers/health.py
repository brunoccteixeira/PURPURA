"""
Health Check endpoints for monitoring API and external data sources
"""
from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", summary="Basic health check")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint

    Returns:
        Status and timestamp
    """
    return {
        "status": "healthy",
        "service": "PÚRPURA API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/integrations", summary="Check external API integrations")
async def integration_health() -> Dict[str, Any]:
    """
    Check health of external Brazilian data sources

    Returns:
        Status for each integration (INPE, ANA, Cemaden)
    """
    from backend.integrations.inpe_client import INPEClient
    from backend.integrations.ana_client import ANAClient

    results = {}

    # Check INPE
    try:
        inpe_client = INPEClient()
        results["inpe"] = inpe_client.health_check()
    except Exception as e:
        results["inpe"] = {
            "service": "INPE",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }

    # Check ANA
    try:
        ana_client = ANAClient()
        results["ana"] = ana_client.health_check()
    except Exception as e:
        results["ana"] = {
            "service": "ANA",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }

    # Cemaden (no API available yet)
    results["cemaden"] = {
        "service": "Cemaden",
        "status": "no_api",
        "note": "No public REST API available - using web scraping or mock data",
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Overall status
    all_ok = all(
        r.get("status") in ["available", "degraded", "no_api"]
        for r in results.values()
    )

    return {
        "overall_status": "healthy" if all_ok else "degraded",
        "integrations": results,
        "timestamp": datetime.utcnow().isoformat(),
    }
