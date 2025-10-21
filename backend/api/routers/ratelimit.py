"""
Rate Limit Administration Endpoints
"""
from fastapi import APIRouter, Request, Response
from typing import Dict, Any
from datetime import datetime

from backend.middleware.rate_limit import limiter, rate_limit_stats, get_identifier

router = APIRouter(prefix="/ratelimit", tags=["Rate Limit"])


@router.get("/stats", summary="Get rate limit statistics")
async def get_rate_limit_stats() -> Dict[str, Any]:
    """
    Get global rate limiting statistics

    Returns:
        Statistics including total requests, limited requests, etc.
    """
    return {
        "stats": rate_limit_stats.get_stats(),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/limits", summary="Get current limits configuration")
async def get_rate_limits() -> Dict[str, Any]:
    """
    Get configured rate limits for different tiers

    Returns:
        Rate limit configuration
    """
    return {
        "tiers": {
            "anonymous": {
                "limit": "60 requests/minute",
                "description": "Default for unauthenticated requests"
            },
            "authenticated": {
                "limit": "300 requests/minute",
                "description": "For authenticated users"
            },
            "premium": {
                "limit": "1000 requests/minute",
                "description": "For premium/paid users"
            },
            "strict": {
                "limit": "10 requests/minute",
                "description": "For expensive operations"
            }
        },
        "storage": rate_limit_stats.get_stats()["storage"],
        "headers": {
            "X-RateLimit-Limit": "Maximum requests allowed",
            "X-RateLimit-Remaining": "Requests remaining in window",
            "X-RateLimit-Reset": "Time when limit resets",
            "Retry-After": "Seconds until you can retry (when limited)"
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/check", summary="Check rate limit status for current identifier")
async def check_rate_limit(request: Request) -> Dict[str, Any]:
    """
    Check current rate limit status for the requesting identifier

    Returns:
        Current usage and limits
    """
    identifier = get_identifier(request)

    # Get current limit info from headers (if available)
    # This is a simplified version - in production you'd query Redis directly
    return {
        "identifier": identifier,
        "message": "Rate limit check successful",
        "note": "Check response headers for X-RateLimit-* information",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/reset/{identifier}", summary="Reset rate limit for identifier")
async def reset_rate_limit(identifier: str) -> Dict[str, Any]:
    """
    Reset rate limit for a specific identifier (admin only)

    Args:
        identifier: The identifier to reset (e.g., ip:127.0.0.1, apikey:abc123)

    Returns:
        Confirmation message

    Note:
        In production, this should require admin authentication
    """
    # TODO: Add admin authentication check
    # TODO: Actually reset the limit in Redis/storage

    return {
        "message": f"Rate limit reset for identifier: {identifier}",
        "identifier": identifier,
        "timestamp": datetime.utcnow().isoformat(),
        "note": "This is a placeholder. Implement actual reset logic with Redis."
    }


@router.get("/test", summary="Test rate limiting")
@limiter.limit("5/minute")  # Strict limit for testing
async def test_rate_limit(request: Request, response: Response) -> Dict[str, Any]:
    """
    Test endpoint with strict rate limit (5 requests/minute)

    Use this to test rate limiting behavior

    Returns:
        Success message if within limits
    """
    identifier = get_identifier(request)

    return {
        "message": "Rate limit test successful",
        "identifier": identifier,
        "limit": "5 requests/minute",
        "tip": "Make 6 requests within a minute to trigger rate limit",
        "timestamp": datetime.utcnow().isoformat(),
    }
