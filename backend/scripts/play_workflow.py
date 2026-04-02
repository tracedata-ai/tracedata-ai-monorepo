"""
Reset datastores (optional) and push a predefined TelemetryPacket sequence to Redis.

See ``docs/workflow_testing.md`` for the full testing guide.

From ``backend/``:

  python scripts/play_workflow.py --fixture scoring_harsh_long_trip
  python scripts/play_workflow.py --fixture minimal_trip --truck TK001 --trip-id TRP-MY-SMOKE
  python scripts/play_workflow.py --json path/to/events.json --truck T12345
  python scripts/play_workflow.py --fixture minimal_trip --no-reset
  python scripts/play_workflow.py --fixture scoring_harsh_long_trip --segments start,smooth,end
  python scripts/play_workflow.py --fixture scoring_harsh_long_trip --start-only
  python scripts/play_workflow.py --list-fixtures
"""

from __future__ import annotations

import argparse
import asyncio
import importlib
import inspect
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

import redis.asyncio as redis
from pydantic import TypeAdapter

from common.config.settings import get_settings
from common.models.events import TelemetryPacket
from common.workflow_fixtures import list_fixtures, resolve_fixture


def _load_json_events(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict) and "events" in raw:
        ev = raw["events"]
        if isinstance(ev, list):
            return ev
    raise ValueError('JSON must be a list of packets or { "events": [ ... ] }')


def _apply_ids(
    packets: list[dict[str, Any]],
    *,
    truck_id: str | None,
    trip_id: str | None,
    driver_id: str | None,
) -> list[dict[str, Any]]:
    if not truck_id and not trip_id and not driver_id:
        return packets
    out: list[dict[str, Any]] = []
    for p in packets:
        q = json.loads(json.dumps(p))
        ev = q.get("event")
        if isinstance(ev, dict):
            if truck_id is not None:
                ev["truck_id"] = truck_id
            if trip_id is not None:
                ev["trip_id"] = trip_id
            if driver_id is not None:
                ev["driver_id"] = driver_id
        out.append(q)
    return out


def _serialize_packet(raw: dict[str, Any]) -> str:
    ta = TypeAdapter(TelemetryPacket)
    model = ta.validate_python(raw)
    return model.model_dump_json()


async def _run(args: argparse.Namespace) -> None:
    settings = get_settings()

    if args.list_fixtures:
        print("Built-in fixtures:")
        for name in list_fixtures():
            print(f"  - {name}")
        return

    if args.fixture:
        mod_path = resolve_fixture(args.fixture)
        mod = importlib.import_module(mod_path)
        build = mod.build_events
        kw: dict[str, Any] = {"anchor": datetime.now(UTC).replace(microsecond=0)}
        if args.trip_id:
            kw["trip_id"] = args.trip_id
        if args.truck:
            kw["truck_id"] = args.truck
        if args.driver:
            kw["driver_id"] = args.driver
        if args.start_only and args.segments is not None:
            raise SystemExit("Use either --start-only or --segments, not both")

        sig_params = inspect.signature(build).parameters

        if "segments" in sig_params:
            if args.start_only:
                kw["segments"] = frozenset({"start"})
            elif args.segments is not None:
                from common.workflow_fixtures.scoring_harsh_long_trip import (
                    parse_trip_segments,
                )

                try:
                    kw["segments"] = parse_trip_segments(args.segments)
                except ValueError as e:
                    raise SystemExit(str(e)) from e
        elif args.start_only or args.segments is not None:
            raise SystemExit(
                f"--start-only / --segments not supported for fixture {args.fixture!r}"
            )

        packets: list[dict[str, Any]] = build(**kw)
    elif args.json:
        packets = _load_json_events(Path(args.json))
        packets = _apply_ids(
            packets,
            truck_id=args.truck,
            trip_id=args.trip_id,
            driver_id=args.driver,
        )
    else:
        raise SystemExit("Pass --fixture <name> or --json <path> (or --list-fixtures)")

    if (args.start_only or args.segments is not None) and not args.fixture:
        raise SystemExit("--start-only / --segments require --fixture")

    if not packets:
        raise SystemExit("No events to push")

    first = TypeAdapter(TelemetryPacket).validate_python(packets[0])
    truck_for_queue = args.truck or first.event.truck_id
    buffer_key = f"telemetry:{truck_for_queue}:buffer"

    if not args.no_reset:
        import scripts.clean_datastores as clean_datastores

        await clean_datastores.main(
            skip_redis=args.skip_redis,
            skip_postgres=args.skip_postgres,
        )
    else:
        client = redis.from_url(settings.redis_url, decode_responses=True)
        try:
            await client.delete(buffer_key)
            print(f"Cleared buffer only: {buffer_key}")
        finally:
            await client.aclose()

    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        for i, raw in enumerate(packets):
            json_str = _serialize_packet(raw)
            await client.zadd(buffer_key, {json_str: i})

        print(f"Pushed {len(packets)} packet(s) to {buffer_key}")
        print(f"  trip_id (first event): {first.event.trip_id}")
        print(f"  truck_id: {truck_for_queue}")
    finally:
        await client.aclose()


def main() -> None:
    p = argparse.ArgumentParser(description="Play a workflow fixture into Redis buffer")
    p.add_argument(
        "--fixture", "-f", help="Registered fixture name (see --list-fixtures)"
    )
    p.add_argument("--json", "-j", help="Path to JSON packet list or {events: [...]}")
    p.add_argument("--truck", "-t", help="Override truck_id on all events / buffer key")
    p.add_argument("--trip-id", help="Override trip_id on all events")
    p.add_argument("--driver", help="Override driver_id on all events")
    p.add_argument(
        "--no-reset",
        action="store_true",
        help="Do not run clean_datastores; only delete this truck's buffer key",
    )
    p.add_argument(
        "--skip-redis",
        action="store_true",
        help="When resetting: only reset Postgres (clean_datastores)",
    )
    p.add_argument(
        "--skip-postgres",
        action="store_true",
        help="When resetting: only flush Redis (clean_datastores)",
    )
    p.add_argument("--list-fixtures", action="store_true")
    p.add_argument(
        "--segments",
        metavar="LIST",
        help=(
            "scoring_harsh_long_trip only: comma-separated subset of "
            "start,smooth,harsh,end,feedback (default: all)"
        ),
    )
    p.add_argument(
        "--start-only",
        action="store_true",
        help="scoring_harsh_long_trip only: same as --segments start",
    )
    args = p.parse_args()
    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
