"""
Performance metrics and monitoring endpoints
"""
from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/cache", summary="Get cache statistics")
async def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache performance statistics

    Returns:
        Cache metrics including hit rate, total entries, etc.
    """
    from backend.integrations.cache import get_cache

    cache = get_cache()
    stats = cache.stats()

    return {
        "cache_stats": stats,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/cache/clear", summary="Clear cache")
async def clear_cache() -> Dict[str, Any]:
    """
    Clear all cache entries

    Returns:
        Number of entries cleared
    """
    from backend.integrations.cache import get_cache

    cache = get_cache()
    count = cache.clear()

    return {
        "message": f"Cache cleared: {count} entries removed",
        "entries_cleared": count,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/cache/cleanup", summary="Cleanup expired entries")
async def cleanup_cache() -> Dict[str, Any]:
    """
    Remove expired cache entries

    Returns:
        Number of expired entries removed
    """
    from backend.integrations.cache import get_cache

    cache = get_cache()
    count = cache.cleanup_expired()

    return {
        "message": f"Cleaned up {count} expired entries",
        "entries_removed": count,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/api-performance", summary="Get API performance metrics")
async def get_api_performance() -> Dict[str, Any]:
    """
    Get performance metrics for all integrated APIs

    Returns:
        Detailed performance data including response times, circuit breaker states, etc.
    """
    from backend.integrations.inpe_client import INPEClient
    from backend.integrations.ana_client import ANAClient
    from backend.integrations.cache import get_cache

    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "cache": get_cache().stats(),
        "apis": {}
    }

    # INPE metrics
    try:
        inpe_client = INPEClient()
        inpe_health = inpe_client.health_check()
        metrics["apis"]["inpe"] = {
            "status": inpe_health.get("status"),
            "response_time_ms": inpe_health.get("response_time_ms"),
            "circuit_breaker": inpe_health.get("circuit_breaker_state"),
        }
    except Exception as e:
        metrics["apis"]["inpe"] = {"error": str(e)}

    # ANA metrics
    try:
        ana_client = ANAClient()
        ana_health = ana_client.health_check()
        metrics["apis"]["ana"] = {
            "status": ana_health.get("status"),
            "response_time_ms": ana_health.get("response_time_ms"),
            "circuit_breaker": ana_health.get("circuit_breaker_state"),
        }
    except Exception as e:
        metrics["apis"]["ana"] = {"error": str(e)}

    return metrics
