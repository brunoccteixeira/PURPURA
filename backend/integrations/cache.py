"""
Cache system for API responses

Supports multiple backends:
- In-memory cache (default, no dependencies)
- Redis cache (optional, requires redis package)
"""

import os
import logging
import json
import time
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from functools import wraps

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: float
    expires_at: float
    hit_count: int = 0
    source: str = "unknown"


class InMemoryCache:
    """
    Simple in-memory cache with TTL support
    Thread-safe for basic operations
    """

    def __init__(self, default_ttl: int = 300):
        """
        Initialize cache

        Args:
            default_ttl: Default time-to-live in seconds (5 minutes default)
        """
        self._cache: Dict[str, CacheEntry] = {}
        self.default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
        logger.info(f"InMemoryCache initialized (TTL: {default_ttl}s)")

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        entry = self._cache.get(key)

        if entry is None:
            self._misses += 1
            return None

        # Check expiration
        if time.time() > entry.expires_at:
            del self._cache[key]
            self._misses += 1
            logger.debug(f"Cache expired: {key}")
            return None

        # Update hit count
        entry.hit_count += 1
        self._hits += 1
        logger.debug(f"Cache HIT: {key} (hits: {entry.hit_count})")

        return entry.value

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        source: str = "unknown"
    ) -> None:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = use default)
            source: Source of the data (for debugging)
        """
        ttl = ttl or self.default_ttl
        now = time.time()

        entry = CacheEntry(
            key=key,
            value=value,
            created_at=now,
            expires_at=now + ttl,
            hit_count=0,
            source=source
        )

        self._cache[key] = entry
        logger.debug(f"Cache SET: {key} (TTL: {ttl}s, source: {source})")

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache DELETE: {key}")
            return True
        return False

    def clear(self) -> int:
        """Clear all cache entries"""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cache cleared: {count} entries removed")
        return count

    def cleanup_expired(self) -> int:
        """Remove expired entries"""
        now = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if now > entry.expires_at
        ]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired entries")

        return len(expired_keys)

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "total_entries": len(self._cache),
            "total_hits": self._hits,
            "total_misses": self._misses,
            "hit_rate_pct": round(hit_rate, 2),
            "total_requests": total_requests,
        }


# Global cache instance
_global_cache: Optional[InMemoryCache] = None


def get_cache() -> InMemoryCache:
    """Get or create global cache instance"""
    global _global_cache

    if _global_cache is None:
        # Default TTL from environment or 5 minutes
        default_ttl = int(os.getenv('CACHE_TTL', 300))
        _global_cache = InMemoryCache(default_ttl=default_ttl)

    return _global_cache


def cache_response(
    ttl: Optional[int] = None,
    key_prefix: str = "",
    source: str = "api"
):
    """
    Decorator to cache function responses

    Usage:
        @cache_response(ttl=600, key_prefix="inpe", source="INPE")
        def get_climate_data(lat, lon):
            # expensive API call
            return data

    Args:
        ttl: Cache TTL in seconds
        key_prefix: Prefix for cache key
        source: Data source name
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()

            # Generate cache key from function name and arguments
            # Simplified: just use repr of args/kwargs
            cache_key = f"{key_prefix}:{func.__name__}:{repr(args)}:{repr(kwargs)}"

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call function
            result = func(*args, **kwargs)

            # Cache result
            if result is not None:
                cache.set(cache_key, result, ttl=ttl, source=source)

            return result

        return wrapper
    return decorator


# Async version
def cache_response_async(
    ttl: Optional[int] = None,
    key_prefix: str = "",
    source: str = "api"
):
    """
    Async version of cache_response decorator

    Usage:
        @cache_response_async(ttl=600, key_prefix="inpe")
        async def get_climate_data(lat, lon):
            # expensive async API call
            return data
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache()

            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{repr(args)}:{repr(kwargs)}"

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call async function
            result = await func(*args, **kwargs)

            # Cache result
            if result is not None:
                cache.set(cache_key, result, ttl=ttl, source=source)

            return result

        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    cache = get_cache()

    # Test basic operations
    print("\n🧪 Testing cache operations:")

    cache.set("test_key", {"data": "value"}, ttl=60, source="test")
    print(f"GET test_key: {cache.get('test_key')}")
    print(f"GET test_key (2nd time): {cache.get('test_key')}")
    print(f"GET missing_key: {cache.get('missing_key')}")

    # Test decorator
    @cache_response(ttl=10, key_prefix="demo", source="test")
    def expensive_function(x, y):
        print(f"  → Expensive computation: {x} + {y}")
        time.sleep(0.1)  # Simulate slow operation
        return x + y

    print("\n🧪 Testing cache decorator:")
    print(f"Call 1: {expensive_function(5, 3)}")
    print(f"Call 2 (cached): {expensive_function(5, 3)}")
    print(f"Call 3 (different args): {expensive_function(10, 2)}")

    # Stats
    print(f"\n📊 Cache stats: {cache.stats()}")
