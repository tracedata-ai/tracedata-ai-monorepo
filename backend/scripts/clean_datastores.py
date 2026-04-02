"""
Wipe Redis and reset PostgreSQL schema (all app tables).

- Redis: FLUSHALL (queues, Celery keys, trip cache, telemetry buffers, etc.)
- Postgres: DROP ALL tables registered on SQLAlchemy Base, then CREATE (like API startup)

Usage (from ``backend/`` with env pointing at your instances):

  REDIS_URL=redis://127.0.0.1:6379/0 \\
  DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/tracedata \\
  python scripts/clean_datastores.py

Docker (API container on compose network):

  docker compose exec -T api python scripts/clean_datastores.py

Destructive. Do not run against production without intent.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

# App root on path when run as ``python scripts/clean_datastores.py`` from backend/
_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

import redis.asyncio as redis
from sqlalchemy import text

import api.models as _models  # noqa: F401 — register all ORM tables
from api.models.base import Base
from common.config.settings import get_settings
from common.db.engine import engine


async def _flush_redis(url: str) -> None:
    client = redis.from_url(url, decode_responses=False)
    try:
        await client.flushall()
    finally:
        await client.aclose()


async def _reset_postgres() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS scoring_schema"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def main(*, skip_redis: bool, skip_postgres: bool) -> None:
    settings = get_settings()
    if not skip_redis:
        print(f"Flushing Redis at {settings.redis_url!r} ...")
        await _flush_redis(settings.redis_url)
        print("Redis: OK (FLUSHALL)")
    else:
        print("Redis: skipped")

    if not skip_postgres:
        print("Resetting PostgreSQL (drop_all + create_all) ...")
        await _reset_postgres()
        print("Postgres: OK")
    else:
        print("Postgres: skipped")

    await engine.dispose()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Clean Redis and/or Postgres dev data")
    p.add_argument("--skip-redis", action="store_true")
    p.add_argument("--skip-postgres", action="store_true")
    args = p.parse_args()
    asyncio.run(main(skip_redis=args.skip_redis, skip_postgres=args.skip_postgres))
