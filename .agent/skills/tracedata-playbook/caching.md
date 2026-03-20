# Caching Strategy: Cache-Aside Standard

This module defines the required caching behavior for TraceData. It is tool-agnostic at the strategy level and currently implemented with Redis.

## Core Pattern

Use Cache-Aside (Look-Aside):

1. Read path checks cache first.
2. If hit, return cached value.
3. If miss, query PostgreSQL (source of truth).
4. Backfill cache with TTL.

## Consistency Rules

### 1. Strict Invalidation on Write

Any successful write operation (update, patch, delete) must invalidate the related key(s) immediately after DB commit.

```python
await db.commit()
await redis.delete(f"vehicle:{vehicle_id}")
```

### 2. Mandatory TTL

Every cache key must include expiration.

- Default TTL: 60 minutes (`3600` seconds)
- Critical TTL: 5 minutes (`300` seconds) for fast-changing state such as active trip summaries

## What to Cache

- Cache: lookup data (tenants, vehicles)
- Cache: auth/session state (bounded by session lifetime)
- Cache: active trip summaries (short TTL)
- Do not cache: high-volume telemetry history (GPS, G-force streams)

## Redis Implementation Notes

- Preferred value format: JSON serialized `STRING`
- Typical command pattern: `SET vehicle:123 "{data}" EX 3600`
- Use pipelining or Lua scripts for bulk invalidation when needed

## Reference

Source document: [docs/01-project-documents/10-caching-strategy.md](../../../docs/01-project-documents/10-caching-strategy.md)
