# PERF002: Redis Caching Strategy

**Category**: caching

## Description

        Implement multi-layer caching with Redis.

        Cache Layers:
        - L1: Application memory (1min TTL)
        - L2: Redis (5min TTL)
        - L3: Database

        Cache Keys:
        - Product: product:{id}
        - Cart: cart:{user_id}
        - Session: session:{token}

        Invalidation:
        - Write-through for critical data
        - TTL-based for read-heavy data
        

## Impact Metrics
```json
{
  "cache_hit_rate": "85%",
  "response_time": "-70%",
  "database_load": "-80%"
}
```
