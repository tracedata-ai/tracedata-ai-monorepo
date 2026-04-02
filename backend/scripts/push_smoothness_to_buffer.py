"""
Push one ``smoothness_log`` (10-min batch stats) packet onto a truck buffer ZSET.

For full trip sequences (validated, ordered), use ``scripts/play_workflow.py``; see
``docs/workflow_testing.md``.

Ingestion reads: telemetry:{truck_id}:buffer

Usage (from ``backend/``):

  REDIS_URL=redis://127.0.0.1:6379/0 python scripts/push_smoothness_to_buffer.py
  python scripts/push_smoothness_to_buffer.py --truck TK002 --trip-id TRIP-MY-TEST-001
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import uuid
from datetime import UTC, datetime

_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

import redis.asyncio as redis

from common.samples.smoothness_batch import (
    build_smoothness_log_packet,
    reference_smoothness_batch_details,
    smoothness_details_mild_variant,
)


async def _run(args: argparse.Namespace) -> None:
    trip_id = args.trip_id or f"TRIP-MANUAL-{uuid.uuid4().hex[:10]}"
    now = datetime.now(UTC)
    dev = f"DEV-SMOOTH-{uuid.uuid4().hex[:12]}"

    details = (
        reference_smoothness_batch_details()
        if args.exact_reference
        else smoothness_details_mild_variant(args.variant_seed)
    )
    packet = build_smoothness_log_packet(
        trip_id=trip_id,
        truck_id=args.truck,
        driver_id=args.driver,
        timestamp=now,
        offset_seconds=args.offset_seconds,
        trip_meter_km=args.trip_meter_km,
        odometer_km=args.odometer_km,
        lat=args.lat,
        lon=args.lon,
        batch_id=args.batch_id or f"BATCH-{args.truck}-{now.strftime('%H%M%S')}",
        event_id=str(uuid.uuid4()),
        device_event_id=dev,
        details=details,
    )

    key = f"telemetry:{args.truck}:buffer"
    client = redis.from_url(args.redis_url, decode_responses=True)
    try:
        score = await client.zcard(key)
        await client.zadd(key, {json.dumps(packet): score})
    finally:
        await client.aclose()

    print("Pushed smoothness_log batch")
    print(f"  Redis key:   {key}")
    print(f"  trip_id:     {trip_id}")
    print(f"  truck_id:    {args.truck}")
    print(f"  device_ev:   {dev}")
    print(f"  event_type:  smoothness_log")
    print()
    print("Watch ingestion/orchestrator logs; processed queue key will be:")
    print(f"  telemetry:{args.truck}:processed")


def main() -> None:
    p = argparse.ArgumentParser(description="ZADD one smoothness_log to telemetry buffer")
    p.add_argument("--redis-url", default=os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0"))
    p.add_argument("--truck", default="TK001", help="Truck id → telemetry:{truck}:buffer")
    p.add_argument("--trip-id", default=None, help="Fixed trip id (default: random TRIP-MANUAL-*)")
    p.add_argument("--driver", default="DRV-DEMO-001")
    p.add_argument("--offset-seconds", type=int, default=600)
    p.add_argument("--trip-meter-km", type=float, default=12.0)
    p.add_argument("--odometer-km", type=float, default=180_012.0)
    p.add_argument("--lat", type=float, default=1.325)
    p.add_argument("--lon", type=float, default=103.875)
    p.add_argument("--batch-id", default=None)
    p.add_argument("--variant-seed", type=int, default=0, help="Jitter seed for smoothness_details_mild_variant")
    p.add_argument(
        "--exact-reference",
        action="store_true",
        help="Use golden details (same numbers as docs); ignore --variant-seed",
    )
    asyncio.run(_run(p.parse_args()))


if __name__ == "__main__":
    main()
