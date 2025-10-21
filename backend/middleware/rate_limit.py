"""
Rate Limiting Middleware for PÚRPURA API

Implements tiered rate limiting with Redis backend:
- Anonymous users: 60 requests/minute
- Authenticated users: 300 requests/minute
- Premium users: 1000 requests/minute

Features:
- Redis-backed storage (distributed)
- In-memory fallback
- Custom rate limit headers
- Per-endpoint overrides
- IP-based and user-based limiting
"""

import os
import logging
from typing import Optional, Callable
from datetime import datetime
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from backend.utils.logging import get_logger

logger = get_logger(__name__)


def get_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting

    Uses this priority:
    1. User ID from authentication (if implemented)
    2. API key from header (if provided)
    3. IP address (fallback)

    Args:
        request: FastAPI request object

    Returns:
        Unique identifier string
    """
    # Check for user authentication (future implementation)
    # if hasattr(request.state, 'user') and request.state.user:
    #     return f"user:{request.state.user.id}"

    # Check for API key
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"apikey:{api_key}"

    # Fallback to IP address
    ip = get_remote_address(request)
    return f"ip:{ip}"


def get_rate_limit_key_func(request: Request) -> str:
    """
    Get Redis key for rate limiting

    Format: ratelimit:{identifier}:{endpoint}

    Args:
        request: FastAPI request object

    Returns:
        Redis key string
    """
    identifier = get_identifier(request)
    endpoint = request.url.path
    return f"ratelimit:{identifier}:{endpoint}"


def get_storage_uri() -> str:
    """
    Get storage URI for rate limiter

    Returns Redis URI if available, otherwise in-memory

    Returns:
        Storage URI string
    """
    cache_backend = os.getenv('CACHE_BACKEND', 'memory').lower()

    if cache_backend == 'redis':
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = os.getenv('REDIS_PORT', 6379)
        redis_db = int(os.getenv('REDIS_DB', 0))
        redis_password = os.getenv('REDIS_PASSWORD')

        if redis_password:
            return f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
        else:
            return f"redis://{redis_host}:{redis_port}/{redis_db}"

    # In-memory storage (not recommended for production)
    return "memory://"


def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom handler for rate limit exceeded errors

    Returns JSON response with retry-after information

    Args:
        request: FastAPI request object
        exc: RateLimitExceeded exception

    Returns:
        JSONResponse with rate limit info
    """
    # Extract retry_after from exception
    retry_after = getattr(exc, 'retry_after', None)

    # Extract limit description from Limit object
    limit_str = "unknown"
    if hasattr(exc, 'limit'):
        limit_obj = exc.limit
        # Try to get the limit string representation
        if hasattr(limit_obj, 'limit'):
            limit_str = limit_obj.limit
        elif hasattr(limit_obj, '_limit'):
            limit_str = limit_obj._limit

    # Calculate retry_after in seconds if available
    retry_seconds = None
    if retry_after:
        try:
            # If retry_after is a datetime, calculate seconds from now
            if hasattr(retry_after, 'timestamp'):
                retry_seconds = int(retry_after.timestamp() - datetime.utcnow().timestamp())
            else:
                retry_seconds = int(retry_after)
        except:
            retry_seconds = 60  # Default to 60 seconds

    identifier = get_identifier(request)

    # Log rate limit exceeded with structured data
    logger.warning(
        "rate_limit_exceeded",
        identifier=identifier,
        endpoint=str(request.url.path),
        method=str(request.method),
        limit=str(limit_str),
        retry_after_seconds=retry_seconds if retry_seconds is not None else None,
        client_ip=str(request.client.host) if request.client else None,
        user_agent=str(request.headers.get("user-agent")) if request.headers.get("user-agent") else None,
    )

    response = JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please slow down.",
            "retry_after_seconds": retry_seconds,
            "limit": str(limit_str),  # Ensure it's a string
            "identifier": str(identifier),
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    # Add rate limit headers
    if retry_seconds:
        response.headers["Retry-After"] = str(retry_seconds)

    return response


# Initialize limiter
try:
    storage_uri = get_storage_uri()
    limiter = Limiter(
        key_func=get_identifier,
        storage_uri=storage_uri,
        default_limits=["60/minute"],  # Default for anonymous users
        headers_enabled=True,
        retry_after="http-date",
        swallow_errors=True  # Don't crash if storage unavailable
    )
    logger.info(
        "rate_limiter_initialized",
        storage_uri=storage_uri,
        default_limit="60/minute",
        headers_enabled=True
    )
except Exception as e:
    logger.warning(
        "rate_limiter_fallback",
        error=str(e),
        error_type=type(e).__name__,
        fallback_storage="memory://",
        message="Failed to initialize rate limiter with configured storage, using in-memory fallback"
    )
    limiter = Limiter(
        key_func=get_identifier,
        storage_uri="memory://",
        default_limits=["60/minute"],
        headers_enabled=True
    )


# Tiered rate limit decorators
def rate_limit_anonymous():
    """
    Rate limit for anonymous users: 60 requests/minute

    Usage:
        @router.get("/public")
        @limiter.limit("60/minute")
        async def public_endpoint():
            pass
    """
    return limiter.limit("60/minute")


def rate_limit_authenticated():
    """
    Rate limit for authenticated users: 300 requests/minute

    Usage:
        @router.get("/authenticated")
        @limiter.limit("300/minute")
        async def authenticated_endpoint():
            pass
    """
    return limiter.limit("300/minute")


def rate_limit_premium():
    """
    Rate limit for premium users: 1000 requests/minute

    Usage:
        @router.get("/premium")
        @limiter.limit("1000/minute")
        async def premium_endpoint():
            pass
    """
    return limiter.limit("1000/minute")


def rate_limit_strict():
    """
    Strict rate limit for expensive operations: 10 requests/minute

    Usage:
        @router.post("/expensive")
        @limiter.limit("10/minute")
        async def expensive_endpoint():
            pass
    """
    return limiter.limit("10/minute")


# Rate limit stats
class RateLimitStats:
    """Track rate limit statistics"""

    def __init__(self):
        self.total_requests = 0
        self.limited_requests = 0
        self.unique_identifiers = set()

    def record_request(self, identifier: str, limited: bool = False):
        """Record a request"""
        self.total_requests += 1
        self.unique_identifiers.add(identifier)
        if limited:
            self.limited_requests += 1

    def get_stats(self):
        """Get statistics"""
        return {
            "total_requests": self.total_requests,
            "limited_requests": self.limited_requests,
            "limit_rate_pct": round(
                (self.limited_requests / self.total_requests * 100) if self.total_requests > 0 else 0,
                2
            ),
            "unique_identifiers": len(self.unique_identifiers),
            "storage": storage_uri,
        }


# Global stats instance
rate_limit_stats = RateLimitStats()


# Middleware to track rate limit usage
async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware to add rate limit headers to all responses

    Args:
        request: FastAPI request
        call_next: Next middleware/handler

    Returns:
        Response with rate limit headers
    """
    identifier = get_identifier(request)
    is_limited = False

    try:
        response = await call_next(request)
    except RateLimitExceeded as e:
        is_limited = True
        response = custom_rate_limit_exceeded_handler(request, e)

    # Record stats
    rate_limit_stats.record_request(identifier, is_limited)

    # Add custom headers
    response.headers["X-Identifier"] = identifier

    return response


# Export
__all__ = [
    'limiter',
    'rate_limit_anonymous',
    'rate_limit_authenticated',
    'rate_limit_premium',
    'rate_limit_strict',
    'custom_rate_limit_exceeded_handler',
    'rate_limit_middleware',
    'rate_limit_stats',
]
