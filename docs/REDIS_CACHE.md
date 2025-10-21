# Redis Cache Configuration Guide

## Overview

PÚRPURA supports two cache backends:
- **InMemoryCache** (default): Fast, local, single-process
- **RedisCache** (recommended for production): Distributed, persistent, multi-process

## Quick Start

### Option 1: Use InMemory Cache (Default)

No configuration needed. Just run the API:

```bash
python -m uvicorn backend.api.main:app --reload
```

### Option 2: Use Redis Cache

#### Start Redis with Docker

```bash
# Start Redis
docker compose up -d redis

# Check Redis is running
docker compose ps redis

# View Redis logs
docker compose logs -f redis
```

#### Configure Environment

Create a `.env` file:

```bash
# Enable Redis cache
CACHE_BACKEND=redis

# Redis connection (defaults shown)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # Leave empty if no password
REDIS_KEY_PREFIX=purpura:

# Cache TTL
CACHE_TTL=300  # 5 minutes default
```

#### Start API with Redis

```bash
# With .env file
python -m uvicorn backend.api.main:app --reload

# Or with environment variables
CACHE_BACKEND=redis python -m uvicorn backend.api.main:app --reload
```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CACHE_BACKEND` | `memory` | Cache backend: `memory` or `redis` |
| `CACHE_TTL` | `300` | Default TTL in seconds |
| `REDIS_HOST` | `localhost` | Redis host |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_DB` | `0` | Redis database number (0-15) |
| `REDIS_PASSWORD` | None | Redis password (if authentication enabled) |
| `REDIS_KEY_PREFIX` | `purpura:` | Prefix for all cache keys |

### Redis Docker Configuration

The `docker-compose.yml` includes:
- **Image**: redis:7-alpine (lightweight)
- **Persistence**: AOF (Append-Only File) enabled
- **Memory**: 256MB limit with LRU eviction
- **Port**: 6379 (exposed to host)
- **Health check**: Every 5 seconds

## Cache Operations

### API Endpoints

```bash
# Get cache statistics
GET /api/v1/metrics/cache

# Clear cache
POST /api/v1/metrics/cache/clear

# Cleanup expired entries (InMemory only, Redis auto-expires)
POST /api/v1/metrics/cache/cleanup

# Full API performance metrics
GET /api/v1/metrics/api-performance
```

### Example: Check Cache Stats

```bash
curl http://localhost:8000/api/v1/metrics/cache | jq
```

**InMemory Response**:
```json
{
  "cache_stats": {
    "total_entries": 5,
    "total_hits": 120,
    "total_misses": 30,
    "hit_rate_pct": 80.0,
    "total_requests": 150
  }
}
```

**Redis Response**:
```json
{
  "cache_stats": {
    "backend": "redis",
    "total_entries": 5,
    "total_hits": 120,
    "total_misses": 30,
    "hit_rate_pct": 80.0,
    "total_requests": 150,
    "redis_version": "7.2.0",
    "connected_clients": 2
  }
}
```

## Performance Comparison

| Metric | InMemory | Redis |
|--------|----------|-------|
| **Latency** | ~0.001ms | ~0.5ms (localhost) |
| **Shared across processes** | ❌ No | ✅ Yes |
| **Persistent across restarts** | ❌ No | ✅ Yes (with AOF) |
| **Memory usage** | Unbounded | Configurable (256MB default) |
| **Eviction policy** | Manual cleanup | LRU automatic |
| **Scalability** | Single process | Multi-server |

## Cache TTLs by Data Type

Configured TTLs in the codebase:

- **INPE Climate Projections**: 3600s (1 hour)
  - Data changes slowly, projections are stable
- **ANA Rainfall Data**: 600s (10 minutes)
  - More dynamic, real-time monitoring
- **Health Checks**: No cache (always fresh)

## Monitoring

### Redis CLI

```bash
# Connect to Redis
docker exec -it purpura-redis redis-cli

# Monitor commands in real-time
MONITOR

# Get all PÚRPURA keys
KEYS purpura:*

# Check specific key
GET purpura:inpe_heat:get_heat_stress_projection:(-23.5505, -46.6333):{'scenario': 'rcp45', 'year': 2050}

# Get key TTL
TTL purpura:inpe_heat:...

# Get stats
INFO stats

# Exit
exit
```

### Logs

```bash
# API logs (cache operations)
tail -f logs/purpura-api.log | grep -i cache

# Redis logs
docker compose logs -f redis
```

## Production Deployment

### Recommended Configuration

```bash
# Use Redis for distributed cache
CACHE_BACKEND=redis

# External Redis service (e.g., AWS ElastiCache, Redis Cloud)
REDIS_HOST=your-redis.amazonaws.com
REDIS_PORT=6379
REDIS_PASSWORD=your-secure-password
REDIS_DB=0

# Longer TTL for production (stable data)
CACHE_TTL=3600

# Namespace per environment
REDIS_KEY_PREFIX=purpura:prod:
```

### Redis Cluster (High Availability)

For production, consider:
- **Redis Cluster**: Automatic sharding and replication
- **Redis Sentinel**: Automatic failover
- **Managed Services**: AWS ElastiCache, Azure Cache for Redis, Redis Cloud

### Security

- Enable Redis AUTH with strong password
- Use TLS/SSL for encrypted connections
- Firewall rules to restrict access
- Separate Redis instance per environment

## Troubleshooting

### "Failed to connect to Redis"

**Cause**: Redis not running or wrong connection settings

**Solution**:
```bash
# Check Redis is running
docker compose ps redis

# Check logs
docker compose logs redis

# Restart Redis
docker compose restart redis
```

### High Memory Usage

**Cause**: Too many cached entries or long TTLs

**Solution**:
```bash
# Manually clear cache
curl -X POST http://localhost:8000/api/v1/metrics/cache/clear

# Or via Redis CLI
docker exec -it purpura-redis redis-cli FLUSHDB
```

### Cache Misses

**Cause**: Cache expired or keys not matching

**Solution**:
- Check TTL settings
- Monitor cache stats for hit rate
- Verify key generation is consistent

## Best Practices

1. **Use Redis in production**: Distributed cache for multiple API instances
2. **Set appropriate TTLs**: Balance freshness vs. performance
3. **Monitor hit rates**: Aim for >70% hit rate
4. **Clear cache after deployments**: Ensure fresh data
5. **Use key prefixes**: Namespace per environment
6. **Configure memory limits**: Prevent unbounded growth
7. **Enable persistence**: AOF for data durability

## Example Integration

```python
from backend.integrations.cache import get_cache, cache_response

# Get cache instance (auto-selected based on env)
cache = get_cache()

# Manual caching
cache.set("my_key", {"data": "value"}, ttl=600)
value = cache.get("my_key")

# Decorator-based caching
@cache_response(ttl=3600, key_prefix="api", source="external")
def expensive_api_call(param):
    # Expensive operation
    return result
```

## Migration

### From InMemory to Redis

1. Start Redis: `docker compose up -d redis`
2. Set environment: `CACHE_BACKEND=redis`
3. Restart API
4. Monitor logs for "✅ Using Redis cache (distributed)"

### From Redis back to InMemory

1. Set environment: `CACHE_BACKEND=memory`
2. Restart API
3. Monitor logs for "✅ Using InMemory cache (local)"

---

**Questions?** Check the logs or run health checks:
```bash
curl http://localhost:8000/api/v1/health/integrations
```
