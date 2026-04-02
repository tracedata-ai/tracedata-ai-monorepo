"""
Trace one truck through buffer → (ingestion worker) → pipeline_events.

Shows production Redis queues and recent rows in ``pipeline_events``. Use this
after ``play_workflow.py`` (with the ingestion worker running).

From ``backend/``:

  uv run python scripts/trace_ingestion.py
  uv run python scripts/trace_ingestion.py --truck T12345 --trip-id TRP-2026-a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6

Flow (see ``core/ingestion/sidecar.py``):

  1. Raw ``TelemetryPacket`` JSON lives in ``telemetry:{truck_id}:buffer`` (sorted set).
  2. ``core.ingestion.worker`` pops into an in-memory ring buffer, then runs the
     sidecar when the batch is ready (size ≥10 or max wait, default 2s).
  3. Sidecar validates, dedupes on ``device_event_id``, inserts into
     ``pipeline_events`` (status ``received``), then enqueues a ``TripEvent`` on
     ``telemetry:{truck_id}:processed``.
  4. Failures go to ``telemetry:{truck_id}:rejected`` (DLQ).

Requires: same ``REDIS_URL`` / ``DATABASE_URL`` as the worker (see ``get_settings()``).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from common.config.settings import get_settings
from common.redis.keys import RedisSchema


async def _run(*, truck_id: str, trip_id: str | None, limit: int) -> None:
    settings = get_settings()
    buf = RedisSchema.Telemetry.buffer(truck_id)
    proc = RedisSchema.Telemetry.processed(truck_id)
    rej = RedisSchema.Telemetry.rejected(truck_id)

    print("settings.redis_url:", settings.redis_url)
    tail = settings.database_url.split("@")[-1]
    print("settings.database_url:", f"...@{tail}")
    print()

    r = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        zb = await r.zcard(buf)
        zp = await r.zcard(proc)
        zr = await r.zcard(rej)
        print("Redis (production keys)")
        print(f"  {buf}     zcard={zb}")
        print(f"  {proc}  zcard={zp}")
        print(f"  {rej}   zcard={zr}")

        if zp > 0:
            row = await r.zrange(proc, 0, 0)
            if row:
                te = json.loads(row[0])
                print("\n  Latest processed TripEvent (lowest score):")
                print(
                    f"    event_type={te.get('event_type')} trip_id={te.get('trip_id')}"
                )
        if zr > 0:
            row = await r.zrange(rej, 0, 0)
            if row:
                dlq = json.loads(row[0])
                print("\n  Latest rejected payload:")
                print(f"    reason={dlq.get('reason')}")
    finally:
        await r.aclose()

    engine = create_async_engine(settings.database_url, echo=False)
    try:
        async with engine.connect() as conn:
            print("\nPostgres pipeline_events")
            if trip_id:
                q = text("""
                    SELECT id, event_type, trip_id, truck_id, status, device_event_id, ingested_at
                    FROM pipeline_events
                    WHERE trip_id = :trip_id
                    ORDER BY id DESC
                    LIMIT :lim
                    """)
                res = await conn.execute(q, {"trip_id": trip_id, "lim": limit})
            else:
                q = text("""
                    SELECT id, event_type, trip_id, truck_id, status, device_event_id, ingested_at
                    FROM pipeline_events
                    WHERE truck_id = :truck_id
                    ORDER BY id DESC
                    LIMIT :lim
                    """)
                res = await conn.execute(q, {"truck_id": truck_id, "lim": limit})
            rows = res.mappings().all()
            if not rows:
                print(
                    "  (no rows — worker not run, rejected, or wrong trip/truck filter)"
                )
            for row in rows:
                print(
                    f"  id={row['id']} {row['event_type']!s:16} "
                    f"trip={row['trip_id']!s} status={row['status']!s} "
                    f"ingested_at={row['ingested_at']}"
                )
    finally:
        await engine.dispose()


def main() -> None:
    p = argparse.ArgumentParser(
        description="Trace Redis telemetry queues → pipeline_events"
    )
    p.add_argument("--truck", "-t", default="T12345", help="Truck id (default: T12345)")
    p.add_argument(
        "--trip-id",
        help="Filter pipeline_events by trip_id (canonical scoring fixture if omitted with --truck only)",
    )
    p.add_argument("--limit", type=int, default=15)
    args = p.parse_args()
    trip = args.trip_id
    asyncio.run(_run(truck_id=args.truck, trip_id=trip, limit=args.limit))


if __name__ == "__main__":
    main()
