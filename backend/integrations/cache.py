"""
Cache system for API responses

Supports multiple backends:
- In-memory cache (default, no dependencies)
- Redis cache (recommended for production, requires redis package)
"""

import os
import logging
import json
import time
import pickle
from typing import Optional, Any, Dict, Protocol
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


class RedisCache:
    """
    Redis-based distributed cache with TTL support

    Benefits over InMemoryCache:
    - Shared across multiple processes/servers
    - Persistent across restarts (configurable)
    - Scalable to large datasets
    - Built-in expiration handling
    """

    def __init__(
        self,
        default_ttl: int = 300,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        key_prefix: str = "purpura:"
    ):
        """
        Initialize Redis cache

        Args:
            default_ttl: Default time-to-live in seconds
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (if required)
            key_prefix: Prefix for all cache keys
        """
        try:
            import redis
        except ImportError:
            raise ImportError(
                "Redis package not installed. Install with: pip install redis[hiredis]"
            )

        self.default_ttl = default_ttl
        self.key_prefix = key_prefix

        # Connect to Redis with connection pooling
        pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=False,  # We'll use pickle for values
            max_connections=10,
            socket_keepalive=True,
            socket_connect_timeout=5,
            health_check_interval=30
        )

        self.client = redis.Redis(connection_pool=pool)

        # Test connection
        try:
            self.client.ping()
            logger.info(
                f"RedisCache initialized: {host}:{port}/{db} (prefix: {key_prefix}, TTL: {default_ttl}s)"
            )
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def _make_key(self, key: str) -> str:
        """Add prefix to key"""
        return f"{self.key_prefix}{key}"

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from Redis cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        try:
            redis_key = self._make_key(key)
            data = self.client.get(redis_key)

            if data is None:
                return None

            # Deserialize with pickle
            value = pickle.loads(data)
            logger.debug(f"Redis cache HIT: {key}")

            # Increment hit counter
            self.client.incr(f"{self.key_prefix}stats:hits")

            return value

        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            self.client.incr(f"{self.key_prefix}stats:misses")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        source: str = "unknown"
    ) -> None:
        """
        Set value in Redis cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = use default)
            source: Source of the data (for debugging)
        """
        try:
            redis_key = self._make_key(key)
            ttl = ttl or self.default_ttl

            # Serialize with pickle
            data = pickle.dumps(value)

            # Set with expiration
            self.client.setex(redis_key, ttl, data)

            logger.debug(f"Redis cache SET: {key} (TTL: {ttl}s, source: {source})")

        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")

    def delete(self, key: str) -> bool:
        """Delete key from Redis cache"""
        try:
            redis_key = self._make_key(key)
            result = self.client.delete(redis_key)
            if result > 0:
                logger.debug(f"Redis cache DELETE: {key}")
                return True
            return False
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False

    def clear(self) -> int:
        """Clear all cache entries with our prefix"""
        try:
            # Find all keys with our prefix
            pattern = f"{self.key_prefix}*"
            keys = list(self.client.scan_iter(match=pattern, count=100))

            # Exclude stats keys
            keys_to_delete = [
                k for k in keys
                if not k.decode().startswith(f"{self.key_prefix}stats:")
            ]

            if keys_to_delete:
                count = self.client.delete(*keys_to_delete)
                logger.info(f"Redis cache cleared: {count} entries removed")
                return count

            return 0

        except Exception as e:
            logger.error(f"Redis CLEAR error: {e}")
            return 0

    def cleanup_expired(self) -> int:
        """
        Redis automatically handles expiration, so this is a no-op

        Returns:
            0 (Redis handles expiration automatically)
        """
        logger.debug("Redis handles expiration automatically")
        return 0

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics from Redis"""
        try:
            # Get Redis info
            info = self.client.info('stats')

            # Get our custom counters
            hits = int(self.client.get(f"{self.key_prefix}stats:hits") or 0)
            misses = int(self.client.get(f"{self.key_prefix}stats:misses") or 0)
            total_requests = hits + misses
            hit_rate = (hits / total_requests * 100) if total_requests > 0 else 0

            # Count keys with our prefix (expensive for large datasets)
            pattern = f"{self.key_prefix}*"
            cursor = 0
            total_entries = 0
            while True:
                cursor, keys = self.client.scan(cursor, match=pattern, count=100)
                # Exclude stats keys
                total_entries += len([
                    k for k in keys
                    if not k.decode().startswith(f"{self.key_prefix}stats:")
                ])
                if cursor == 0:
                    break

            return {
                "backend": "redis",
                "total_entries": total_entries,
                "total_hits": hits,
                "total_misses": misses,
                "hit_rate_pct": round(hit_rate, 2),
                "total_requests": total_requests,
                "redis_version": info.get('redis_version', 'unknown'),
                "connected_clients": info.get('connected_clients', 0),
            }

        except Exception as e:
            logger.error(f"Redis STATS error: {e}")
            return {
                "backend": "redis",
                "error": str(e)
            }

    def ping(self) -> bool:
        """Check if Redis is reachable"""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis PING error: {e}")
            return False


# Global cache instance
_global_cache: Optional[Any] = None  # Can be InMemoryCache or RedisCache


def get_cache():
    """
    Get or create global cache instance

    Returns InMemoryCache or RedisCache based on environment variables:
    - CACHE_BACKEND=redis: Use Redis cache (recommended for production)
    - CACHE_BACKEND=memory: Use in-memory cache (default for development)

    Environment variables for Redis:
    - REDIS_HOST: Redis host (default: localhost)
    - REDIS_PORT: Redis port (default: 6379)
    - REDIS_DB: Redis database number (default: 0)
    - REDIS_PASSWORD: Redis password (optional)
    - CACHE_TTL: Default TTL in seconds (default: 300)

    Returns:
        Cache instance (InMemoryCache or RedisCache)
    """
    global _global_cache

    if _global_cache is None:
        cache_backend = os.getenv('CACHE_BACKEND', 'memory').lower()
        default_ttl = int(os.getenv('CACHE_TTL', 300))

        if cache_backend == 'redis':
            try:
                _global_cache = RedisCache(
                    default_ttl=default_ttl,
                    host=os.getenv('REDIS_HOST', 'localhost'),
                    port=int(os.getenv('REDIS_PORT', 6379)),
                    db=int(os.getenv('REDIS_DB', 0)),
                    password=os.getenv('REDIS_PASSWORD'),
                    key_prefix=os.getenv('REDIS_KEY_PREFIX', 'purpura:')
                )
                logger.info("✅ Using Redis cache (distributed)")
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Redis cache: {e}. "
                    f"Falling back to InMemoryCache"
                )
                _global_cache = InMemoryCache(default_ttl=default_ttl)
        else:
            _global_cache = InMemoryCache(default_ttl=default_ttl)
            logger.info("✅ Using InMemory cache (local)")

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
