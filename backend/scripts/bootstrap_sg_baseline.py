"""
Idempotent Singapore baseline bootstrap for local Docker runs.

Creates baseline entities:
- 1 tenant
- 10 drivers (paired 1:1 with vehicles)
- 10 trucks
- 20 routes

And pushes one baseline trip workflow per driver/vehicle pair to Redis buffer.
Each trip is first written as a real Trip row (UUID PK) in the domain `trips`
table so that simulated telemetry is grounded in the actual DB records.

Telemetry packet IDs used:
  trip_id   → str(Trip.id)             — UUID from domain trips table
  truck_id  → Vehicle.license_plate    — e.g. "SGB001T"
  driver_id → str(Driver.id)           — real UUID (PII-scrubbed in pipeline)

Event flow per loop:
  start -> 3 harsh -> 12-18 smooth (default 15) -> end -> feedback
"""

from __future__ import annotations

import argparse
import asyncio
import importlib
import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any, Callable

import redis.asyncio as redis
from sqlalchemy import select, text

from api.models.driver import Driver
from api.models.fleet import Vehicle
from api.models.route import Route
from api.models.tenant import Tenant
from api.models.trip import Trip
from common.config.settings import get_settings
from common.db.engine import AsyncSessionLocal, engine
from common.models.sa_base import Base

BOOTSTRAP_MARKER_KEY = "td:bootstrap:sg_baseline:v1"
TENANT_NAME = "TraceData Singapore Fleet"


def _sg_route_pairs() -> list[tuple[str, str]]:
    return [
        ("Tuas Logistics Hub", "Jurong Port"),
        ("Jurong Port", "Pioneer"),
        ("Pioneer", "Bukit Batok"),
        ("Bukit Batok", "Woodlands"),
        ("Woodlands", "Yishun"),
        ("Yishun", "Seletar"),
        ("Seletar", "Paya Lebar"),
        ("Paya Lebar", "Changi Cargo"),
        ("Changi Cargo", "Pasir Ris"),
        ("Pasir Ris", "Hougang"),
        ("Hougang", "Serangoon"),
        ("Serangoon", "Toa Payoh"),
        ("Toa Payoh", "Bishan"),
        ("Bishan", "Novena"),
        ("Novena", "Orchard"),
        ("Orchard", "Newton"),
        ("Newton", "Queenstown"),
        ("Queenstown", "HarbourFront"),
        ("HarbourFront", "Marina Bay"),
        ("Marina Bay", "Tuas Logistics Hub"),
    ]


async def _ensure_baseline_entities() -> tuple[list[Driver], list[Vehicle], list[Route]]:
    """
    Idempotently create tenant, 10 drivers, 10 vehicles, 20 routes.
    Also pairs each driver to a vehicle (sets driver.vehicle_id) so that
    every driver has an assigned truck — required for grounded simulation.
    Returns (drivers[:10], vehicles[:10], routes).
    """
    async with AsyncSessionLocal() as session:
        # ── Tenant ──────────────────────────────────────────────────────────
        tenant = (
            await session.execute(select(Tenant).where(Tenant.name == TENANT_NAME))
        ).scalar_one_or_none()
        if tenant is None:
            tenant = Tenant(
                name=TENANT_NAME,
                contact_email="ops@tracedata.sg",
                status="active",
            )
            session.add(tenant)
            await session.flush()

        drivers = (
            (await session.execute(select(Driver).where(Driver.tenant_id == tenant.id)))
            .scalars()
            .all()
        )
        vehicles = (
            (await session.execute(select(Vehicle).where(Vehicle.tenant_id == tenant.id)))
            .scalars()
            .all()
        )
        routes = (
            (await session.execute(select(Route).where(Route.tenant_id == tenant.id)))
            .scalars()
            .all()
        )

        # ── Drivers ─────────────────────────────────────────────────────────
        if len(drivers) < 10:
            for i in range(len(drivers) + 1, 11):
                session.add(
                    Driver(
                        tenant_id=tenant.id,
                        first_name=f"Driver{i:02d}",
                        last_name="SG",
                        email=f"driver{i:02d}@tracedata.sg",
                        license_number=f"SGDL-{i:04d}",
                        status="active",
                        experience_level="intermediate",
                    )
                )

        # ── Vehicles ─────────────────────────────────────────────────────────
        if len(vehicles) < 10:
            for i in range(len(vehicles) + 1, 11):
                session.add(
                    Vehicle(
                        tenant_id=tenant.id,
                        license_plate=f"SGB{i:03d}T",
                        make="Isuzu",
                        model="N-Series",
                        year=2023,
                        status="active",
                        vin=f"SGTRACE{i:010d}",
                    )
                )

        # ── Routes ───────────────────────────────────────────────────────────
        existing_route_names = {r.name for r in routes}
        pairs = _sg_route_pairs()
        for idx, (start, end) in enumerate(pairs, start=1):
            name = f"SG Route {idx:02d}"
            if name in existing_route_names:
                continue
            session.add(
                Route(
                    tenant_id=tenant.id,
                    name=name,
                    start_location=start,
                    end_location=end,
                    distance_km=Decimal(str(8 + (idx % 15))),
                    route_type="mixed",
                )
            )

        await session.commit()

        # Re-fetch after inserts
        drivers = (
            (await session.execute(select(Driver).where(Driver.tenant_id == tenant.id)))
            .scalars()
            .all()
        )
        vehicles = (
            (await session.execute(select(Vehicle).where(Vehicle.tenant_id == tenant.id)))
            .scalars()
            .all()
        )
        routes = (
            (await session.execute(select(Route).where(Route.tenant_id == tenant.id)))
            .scalars()
            .all()
        )
        drivers = drivers[:10]
        vehicles = vehicles[:10]

        # ── Pair drivers to vehicles (1:1) ───────────────────────────────────
        # Assign driver.vehicle_id if not already set so every driver has a truck.
        needs_commit = False
        for driver, vehicle in zip(drivers, vehicles):
            if driver.vehicle_id != vehicle.id:
                driver.vehicle_id = vehicle.id
                needs_commit = True
        if needs_commit:
            await session.commit()

        return list(drivers), list(vehicles), list(routes)


async def _create_trip(
    tenant_id: Any,
    driver: Driver,
    vehicle: Vehicle,
    route: Route | None,
) -> Trip:
    """Insert a real Trip row and return it with its assigned UUID."""
    async with AsyncSessionLocal() as session:
        trip = Trip(
            tenant_id=tenant_id,
            driver_id=driver.id,
            vehicle_id=vehicle.id,
            route_id=route.id if route else None,
            status="active",
        )
        session.add(trip)
        await session.commit()
        await session.refresh(trip)
        return trip


async def _push_trip_batch(
    client: redis.Redis,
    build_events: Callable[..., list[dict[str, Any]]],
    *,
    truck_count: int = 10,
    event_delay: float = 0.5,
    truck_delay: float = 5.0,
) -> int:
    """
    Push one batch of trips (one per active driver/vehicle pair) to the Redis buffer.

    Each trip is first created as a real Trip row in the domain `trips` table,
    so the simulated telemetry is grounded in actual DB records:
      - trip_id   = str(Trip.id)            UUID primary key
      - truck_id  = Vehicle.license_plate   e.g. "SGB001T"
      - driver_id = str(Driver.id)          real UUID (anonymised later by PII scrubber)

    Events are pushed one at a time with `event_delay` seconds between each, and
    `truck_delay` seconds between trucks — preventing the pipeline from being flooded.

    Counts per trip are randomised within realistic bounds:
      smooth_count: 6–24  (10-minute telemetry windows)
      harsh_count:  2–6   (harsh driving incidents)
    """
    import random as _random

    drivers, vehicles, routes = await _ensure_baseline_entities()

    if not drivers:
        return 0
    tenant_id = drivers[0].tenant_id

    # Clamp to available drivers and requested count
    n = max(1, min(truck_count, len(drivers)))
    pairs = list(zip(drivers[:n], vehicles[:n], strict=False))

    now = datetime.now(UTC).replace(microsecond=0)
    total_pushed = 0
    rng = _random.Random()

    for idx, (driver, vehicle) in enumerate(pairs):
        route = routes[idx % len(routes)] if routes else None
        trip = await _create_trip(tenant_id, driver, vehicle, route)

        trip_id = str(trip.id)
        truck_id = vehicle.license_plate
        driver_id = str(driver.id)

        # Randomise trip profile per truck so historic data has natural variance
        trip_smooth = rng.randint(6, 24)
        trip_harsh = rng.randint(2, 6)

        # Stagger trip anchors by 2 minutes so timestamps don't collide
        anchor = now + timedelta(minutes=idx * 2)
        packets = build_events(
            trip_id=trip_id,
            truck_id=truck_id,
            driver_id=driver_id,
            anchor=anchor,
            smooth_count=trip_smooth,
            harsh_count=trip_harsh,
        )

        key = f"telemetry:{truck_id}:buffer"
        for score, packet in enumerate(packets):
            await client.zadd(key, {json.dumps(packet): score})
            total_pushed += 1
            if event_delay > 0:
                await asyncio.sleep(event_delay)

        print(
            f"[sim]   truck={truck_id} trip={trip_id[:8]}… "
            f"events={len(packets)} (smooth={trip_smooth} harsh={trip_harsh})"
        )

        if truck_delay > 0 and idx < len(drivers) - 1:
            await asyncio.sleep(truck_delay)

    return total_pushed


async def _push_baseline_trip_packets() -> int:
    """One-shot baseline push (guarded by marker key). Used in non-loop mode."""
    settings = get_settings()
    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        if await client.get(BOOTSTRAP_MARKER_KEY):
            return 0

        fixture_mod = importlib.import_module(
            "common.workflow_fixtures.sg_baseline_trip"
        )

        pushed = await _push_trip_batch(
            client,
            fixture_mod.build_events,
        )
        await client.set(BOOTSTRAP_MARKER_KEY, "ok")
        return pushed
    finally:
        await client.aclose()


async def _run() -> None:
    # Ensure tables exist when running before FastAPI lifespan startup.
    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS scoring_schema"))
        await conn.run_sync(Base.metadata.create_all)

    pushed = await _push_baseline_trip_packets()
    if pushed:
        print(f"Bootstrap complete: pushed {pushed} telemetry packets.")
    else:
        print("Bootstrap skipped: marker already present.")


async def _run_loop(
    interval: int,
    event_delay: float,
    truck_delay: float,
    truck_count: int,
) -> None:
    """
    Continuously push trip batches, each grounded in real DB records.

    Each iteration:
      1. Queries active drivers + their assigned vehicles from DB
      2. Creates a Trip row per driver (real UUID, proper FKs)
      3. Pushes events one-at-a-time (event_delay between events,
         truck_delay between trucks) to avoid overwhelming the pipeline
      4. Sleeps for `interval` seconds before next batch

    When called as a sidecar from the FastAPI lifespan, tables and baseline
    entities are already set up — _ensure_baseline_entities() is idempotent.
    """
    fixture_mod = importlib.import_module("common.workflow_fixtures.sg_baseline_trip")
    build_events = fixture_mod.build_events

    settings = get_settings()
    loop_num = 0

    print(
        f"[sim] Starting continuous simulation "
        f"(trucks={truck_count} interval={interval}s "
        f"event_delay={event_delay}s truck_delay={truck_delay}s)"
    )

    while True:
        loop_num += 1
        client = redis.from_url(settings.redis_url, decode_responses=True)
        try:
            pushed = await _push_trip_batch(
                client,
                build_events,
                truck_count=truck_count,
                event_delay=event_delay,
                truck_delay=truck_delay,
            )
            print(f"[sim] Loop {loop_num}: pushed {pushed} packets total")
        finally:
            await client.aclose()

        await asyncio.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bootstrap SG baseline entities and events."
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Run continuously, pushing a new batch of trips on each iteration.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Seconds to wait between batches in loop mode (default: 30).",
    )
    parser.add_argument(
        "--event-delay",
        type=float,
        default=0.5,
        help="Seconds between individual events within a truck (default: 0.5).",
    )
    parser.add_argument(
        "--truck-delay",
        type=float,
        default=5.0,
        help="Seconds between trucks in a batch (default: 5.0).",
    )
    parser.add_argument(
        "--truck-count",
        type=int,
        default=10,
        help="Number of trucks (driver/vehicle pairs) to simulate per batch (default: 10).",
    )
    args = parser.parse_args()

    if args.loop:
        asyncio.run(_run_loop(args.interval, args.event_delay, args.truck_delay, args.truck_count))
    else:
        asyncio.run(_run())


if __name__ == "__main__":
    main()
