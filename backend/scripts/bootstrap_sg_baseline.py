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
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

import redis.asyncio as redis
from sqlalchemy import select, text

import random as _random
from datetime import date

from api.models.driver import Driver
from api.models.fleet import Vehicle
from api.models.maintenance import Maintenance
from api.models.route import Route
from api.models.tenant import Tenant
from api.models.trip import Trip
from common.config.settings import get_settings
from common.db.engine import AsyncSessionLocal, engine
from common.models.sa_base import Base

BOOTSTRAP_MARKER_KEY = "td:bootstrap:sg_baseline:v1"
TENANT_NAME = "TraceData Singapore Fleet"

_AGENT_SCHEMAS = (
    "scoring_schema",
    "safety_schema",
    "coaching_schema",
    "sentiment_schema",
)


async def reset_for_demo() -> None:
    """
    Hard-reset for reproducible demo restarts.

    Drops every managed table and agent schema, then flushes Redis so each
    boot starts from a completely clean slate.  Call this BEFORE create_all().

    NOTE: All ORM model classes must be imported before calling this so that
    Base.metadata knows about every table.  In main.py, `import api.models`
    handles that.
    """
    async with engine.begin() as conn:
        # Drop all SQLAlchemy-managed tables (domain + pipeline ORM models)
        await conn.run_sync(Base.metadata.drop_all)
        # Drop agent-owned schemas and everything inside them
        for schema in _AGENT_SCHEMAS:
            await conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))

    # Flush Redis so no stale telemetry buffers, processed queues, or marker keys remain
    settings = get_settings()
    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await client.flushdb()
    finally:
        await client.aclose()


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


_SG_LOCATION_COORDS: dict[str, tuple[float, float]] = {
    "Tuas Logistics Hub": (1.2990, 103.6360),
    "Jurong Port":        (1.3230, 103.7080),
    "Pioneer":            (1.3360, 103.7100),
    "Bukit Batok":        (1.3490, 103.7490),
    "Woodlands":          (1.4390, 103.7860),
    "Yishun":             (1.4290, 103.8350),
    "Seletar":            (1.4050, 103.8690),
    "Paya Lebar":         (1.3180, 103.8930),
    "Changi Cargo":       (1.3560, 103.9880),
    "Pasir Ris":          (1.3730, 103.9490),
    "Hougang":            (1.3710, 103.8930),
    "Serangoon":          (1.3500, 103.8730),
    "Toa Payoh":          (1.3320, 103.8460),
    "Bishan":             (1.3520, 103.8490),
    "Novena":             (1.3200, 103.8440),
    "Orchard":            (1.3040, 103.8318),
    "Newton":             (1.3120, 103.8390),
    "Queenstown":         (1.2940, 103.8060),
    "HarbourFront":       (1.2650, 103.8200),
    "Marina Bay":         (1.2840, 103.8607),
}


_ROUTE_WAYPOINTS: dict[tuple[str, str], list[dict]] = {
    ("Tuas Logistics Hub", "Jurong Port"): [
        {"lat": 1.3050, "lon": 103.6580, "name": "Tuas South Ave"},
        {"lat": 1.3140, "lon": 103.6780, "name": "Joo Koon MRT"},
    ],
    ("Jurong Port", "Pioneer"): [
        {"lat": 1.3280, "lon": 103.7060, "name": "Pioneer Rd junction"},
    ],
    ("Pioneer", "Bukit Batok"): [
        {"lat": 1.3380, "lon": 103.7210, "name": "Jurong East MRT"},
        {"lat": 1.3450, "lon": 103.7370, "name": "Bukit Batok West Ave"},
    ],
    ("Bukit Batok", "Woodlands"): [
        {"lat": 1.3620, "lon": 103.7540, "name": "Choa Chu Kang MRT"},
        {"lat": 1.4000, "lon": 103.7700, "name": "Kranji Expressway"},
    ],
    ("Woodlands", "Yishun"): [
        {"lat": 1.4420, "lon": 103.8010, "name": "Admiralty"},
        {"lat": 1.4390, "lon": 103.8200, "name": "Sembawang"},
    ],
    ("Yishun", "Seletar"): [
        {"lat": 1.4190, "lon": 103.8480, "name": "Yishun Ave 2"},
        {"lat": 1.4110, "lon": 103.8590, "name": "Seletar Aerospace Park"},
    ],
    ("Seletar", "Paya Lebar"): [
        {"lat": 1.3840, "lon": 103.8750, "name": "Hougang Ave 8"},
        {"lat": 1.3560, "lon": 103.8860, "name": "Bartley Rd"},
    ],
    ("Paya Lebar", "Changi Cargo"): [
        {"lat": 1.3310, "lon": 103.9290, "name": "Tampines Ave 10"},
        {"lat": 1.3530, "lon": 103.9650, "name": "Loyang Ave"},
    ],
    ("Changi Cargo", "Pasir Ris"): [
        {"lat": 1.3620, "lon": 103.9850, "name": "Pasir Ris Dr 12"},
    ],
    ("Pasir Ris", "Hougang"): [
        {"lat": 1.3720, "lon": 103.9490, "name": "Tampines Ave 5"},
        {"lat": 1.3720, "lon": 103.9200, "name": "TPE Exit 4"},
    ],
    ("Hougang", "Serangoon"): [
        {"lat": 1.3630, "lon": 103.8880, "name": "Serangoon North Ave"},
    ],
    ("Serangoon", "Toa Payoh"): [
        {"lat": 1.3450, "lon": 103.8680, "name": "Upper Serangoon Rd"},
        {"lat": 1.3390, "lon": 103.8570, "name": "Braddell Rd"},
    ],
    ("Toa Payoh", "Bishan"): [
        {"lat": 1.3390, "lon": 103.8470, "name": "Toa Payoh Rise"},
    ],
    ("Bishan", "Novena"): [
        {"lat": 1.3440, "lon": 103.8460, "name": "CTE Bishan"},
        {"lat": 1.3310, "lon": 103.8430, "name": "Thomson Rd"},
    ],
    ("Novena", "Orchard"): [
        {"lat": 1.3140, "lon": 103.8390, "name": "Newton Circus"},
    ],
    ("Orchard", "Newton"): [
        {"lat": 1.3070, "lon": 103.8360, "name": "Scotts Rd"},
    ],
    ("Newton", "Queenstown"): [
        {"lat": 1.3050, "lon": 103.8280, "name": "River Valley Rd"},
        {"lat": 1.2980, "lon": 103.8130, "name": "Commonwealth Ave"},
    ],
    ("Queenstown", "HarbourFront"): [
        {"lat": 1.2870, "lon": 103.8090, "name": "Alexandra Rd"},
        {"lat": 1.2760, "lon": 103.8140, "name": "Telok Blangah Rd"},
    ],
    ("HarbourFront", "Marina Bay"): [
        {"lat": 1.2720, "lon": 103.8390, "name": "Keppel Rd"},
        {"lat": 1.2780, "lon": 103.8530, "name": "Marina Coastal Expressway"},
    ],
    ("Marina Bay", "Tuas Logistics Hub"): [
        {"lat": 1.2890, "lon": 103.8200, "name": "AYE West Coast"},
        {"lat": 1.2960, "lon": 103.7500, "name": "AYE Clementi"},
        {"lat": 1.2990, "lon": 103.7000, "name": "AYE Tuas approach"},
    ],
}


async def _ensure_baseline_entities() -> (
    tuple[list[Driver], list[Vehicle], list[Route]]
):
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
            (
                await session.execute(
                    select(Vehicle).where(Vehicle.tenant_id == tenant.id)
                )
            )
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
            s_lat, s_lon = _SG_LOCATION_COORDS.get(start, (1.3521, 103.8198))
            e_lat, e_lon = _SG_LOCATION_COORDS.get(end, (1.3521, 103.8198))
            session.add(
                Route(
                    tenant_id=tenant.id,
                    name=name,
                    start_location=start,
                    end_location=end,
                    distance_km=Decimal(str(8 + (idx % 15))),
                    route_type="mixed",
                    start_lat=s_lat,
                    start_lon=s_lon,
                    end_lat=e_lat,
                    end_lon=e_lon,
                    waypoints=_ROUTE_WAYPOINTS.get((start, end)),
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
            (
                await session.execute(
                    select(Vehicle).where(Vehicle.tenant_id == tenant.id)
                )
            )
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


_MAINT_TYPES = [
    "oil_change",
    "tyre_rotation",
    "brake_inspection",
    "air_filter_replacement",
    "coolant_flush",
    "transmission_service",
    "battery_check",
    "wheel_alignment",
]

_MAINT_STATUSES = ["completed", "completed", "scheduled", "overdue", "in_progress"]


async def _seed_vehicle_details(vehicles: list[Vehicle]) -> None:
    """
    Idempotent: skips if maintenance records already exist.
    For each vehicle:
      - assigns a randomised fuel_level (15–95 %)
      - creates 2–3 maintenance records with realistic statuses
      - sets vehicle.status = 'in_maintenance' when a record is in_progress
    """
    rng = _random.Random(42)
    today = date.today()

    async with AsyncSessionLocal() as session:
        existing = (await session.execute(select(Maintenance).limit(1))).scalar_one_or_none()
        if existing:
            return

        for v in vehicles:
            # Refresh into this session
            vehicle = await session.get(Vehicle, v.id)
            if not vehicle:
                continue

            vehicle.fuel_level = rng.randint(15, 95)

            record_count = rng.randint(2, 3)
            has_in_progress = False
            for j in range(record_count):
                maint_status = rng.choice(_MAINT_STATUSES)
                maint_type = _MAINT_TYPES[(vehicles.index(v) + j) % len(_MAINT_TYPES)]

                scheduled = today + timedelta(days=rng.randint(-30, 60))
                completed = (
                    scheduled + timedelta(days=rng.randint(0, 5))
                    if maint_status == "completed"
                    else None
                )

                session.add(Maintenance(
                    tenant_id=vehicle.tenant_id,
                    vehicle_id=vehicle.id,
                    maintenance_type=maint_type,
                    status=maint_status,
                    scheduled_date=scheduled,
                    completed_date=completed,
                    triggered_by="schedule",
                    notes=f"Routine {maint_type.replace('_', ' ')} — seeded by bootstrap",
                ))

                if maint_status == "in_progress":
                    has_in_progress = True

            if has_in_progress:
                vehicle.status = "in_maintenance"

        await session.commit()
        print(f"[bootstrap] Seeded fuel levels and maintenance records for {len(vehicles)} vehicles.")


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

    # Only dispatch trips for active vehicles — in_maintenance vehicles sit out
    active_pairs = [
        (d, v) for d, v in zip(drivers, vehicles, strict=False)
        if v.status != "in_maintenance"
    ]
    n = max(1, min(truck_count, len(active_pairs)))
    pairs = active_pairs[:n]

    now = datetime.now(UTC).replace(microsecond=0)
    total_pushed = 0
    rng = _random.Random()

    # Guaranteed style rotation so every batch covers the full score spectrum.
    # Cycles: excellent → good → average → poor → aggressive → good → average …
    _STYLE_ROTATION = ["excellent", "good", "average", "poor", "aggressive"]

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
        style = _STYLE_ROTATION[idx % len(_STYLE_ROTATION)]
        packets = build_events(
            trip_id=trip_id,
            truck_id=truck_id,
            driver_id=driver_id,
            anchor=anchor,
            smooth_count=trip_smooth,
            harsh_count=trip_harsh,
            style=style,
        )

        key = f"telemetry:{truck_id}:buffer"
        for score, packet in enumerate(packets):
            await client.zadd(key, {json.dumps(packet): score})
            total_pushed += 1
            if event_delay > 0:
                await asyncio.sleep(event_delay)

        print(
            f"[sim]   truck={truck_id} trip={trip_id[:8]}… "
            f"events={len(packets)} (smooth={trip_smooth} harsh={trip_harsh} style={style})"
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


_AGENT_DDL: list[str] = [
    "CREATE SCHEMA IF NOT EXISTS safety_schema",
    """CREATE TABLE IF NOT EXISTS safety_schema.harsh_events_analysis (
        id SERIAL PRIMARY KEY,
        event_id VARCHAR(80) NOT NULL,
        trip_id VARCHAR(100) NOT NULL,
        event_type VARCHAR(80),
        severity VARCHAR(50),
        event_timestamp TIMESTAMP,
        lat DOUBLE PRECISION,
        lon DOUBLE PRECISION,
        location_name TEXT,
        traffic_conditions TEXT,
        weather_conditions TEXT,
        analysis JSONB,
        created_at TIMESTAMP
    )""",
    "ALTER TABLE safety_schema.harsh_events_analysis ADD COLUMN IF NOT EXISTS location_name TEXT",
    """CREATE TABLE IF NOT EXISTS safety_schema.safety_decisions (
        decision_id SERIAL PRIMARY KEY,
        event_id VARCHAR(80),
        trip_id VARCHAR(100) NOT NULL,
        decision VARCHAR(255),
        action VARCHAR(255),
        reason TEXT,
        recommended_action TEXT,
        created_at TIMESTAMP
    )""",
    "CREATE SCHEMA IF NOT EXISTS coaching_schema",
    """CREATE TABLE IF NOT EXISTS coaching_schema.coaching (
        coaching_id SERIAL PRIMARY KEY,
        trip_id VARCHAR(80) NOT NULL,
        driver_id VARCHAR(80) NOT NULL,
        coaching_category VARCHAR(80),
        message TEXT,
        priority VARCHAR(20),
        created_at TIMESTAMP
    )""",
    "CREATE SCHEMA IF NOT EXISTS sentiment_schema",
    """CREATE TABLE IF NOT EXISTS sentiment_schema.feedback_sentiment (
        sentiment_id SERIAL PRIMARY KEY,
        trip_id VARCHAR(80) NOT NULL,
        driver_id VARCHAR(80) NOT NULL,
        feedback_text TEXT,
        sentiment_score DOUBLE PRECISION,
        sentiment_label VARCHAR(50),
        analysis JSONB,
        created_at TIMESTAMP
    )""",
]


async def _run() -> None:
    # Ensure tables exist when running before FastAPI lifespan startup.
    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS scoring_schema"))
        await conn.run_sync(Base.metadata.create_all)
        # Idempotent migration: add fuel_level if the column was added after first boot
        await conn.execute(text(
            "ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS fuel_level SMALLINT NOT NULL DEFAULT 100"
        ))
        for col, typ in [
            ("start_lat", "DOUBLE PRECISION"),
            ("start_lon", "DOUBLE PRECISION"),
            ("end_lat",   "DOUBLE PRECISION"),
            ("end_lon",   "DOUBLE PRECISION"),
        ]:
            await conn.execute(text(
                f"ALTER TABLE routes ADD COLUMN IF NOT EXISTS {col} {typ}"
            ))
        await conn.execute(text(
            "ALTER TABLE routes ADD COLUMN IF NOT EXISTS waypoints JSONB"
        ))
        # Apply agent-owned schemas (each statement run separately — asyncpg restriction)
        for ddl in _AGENT_DDL:
            await conn.execute(text(ddl))

    _, vehicles, _ = await _ensure_baseline_entities()
    await _seed_vehicle_details(vehicles)

    pushed = await _push_baseline_trip_packets()
    if pushed:
        print(f"Bootstrap complete: pushed {pushed} telemetry packets.")
    else:
        print("Bootstrap skipped: marker already present.")


async def _run_loop(
    event_delay: float,
    truck_delay: float,
    truck_count: int,
    warmup_interval: int = 300,
    steady_interval: int = 3600,
    warmup_hours: float = 2.0,
) -> None:
    """
    Adaptive simulation sidecar — two-phase rate control to stay within LLM RPD limits.

    Phase 1 — Warmup (first `warmup_hours`):
      Small batches every `warmup_interval` seconds (default 5 min).
      Generates just enough data to populate dashboards quickly.

    Phase 2 — Steady-state (after `warmup_hours`):
      Same batch size but sleeps `steady_interval` seconds (default 1 hr).
      Keeps the system alive for K8s liveness checks without burning rate limits.

    Per-batch LLM budget (2 trucks × ~4 harsh events × 2 calls + scoring + coaching):
      ~50 calls/batch × 12 batches/hr (warmup) = ~600 calls/hr  ← safe
      ~50 calls/batch × 1 batch/hr  (steady)   = ~50 calls/hr   ← very safe
    """
    fixture_mod = importlib.import_module("common.workflow_fixtures.sg_baseline_trip")
    build_events = fixture_mod.build_events

    settings = get_settings()
    loop_num = 0
    started_at = asyncio.get_event_loop().time()
    warmup_seconds = warmup_hours * 3600

    phase = "warmup"
    print(
        f"[sim] Starting adaptive simulation — "
        f"warmup: {truck_count} trucks every {warmup_interval}s for {warmup_hours}h, "
        f"then steady: every {steady_interval}s"
    )

    while True:
        elapsed = asyncio.get_event_loop().time() - started_at
        new_phase = "warmup" if elapsed < warmup_seconds else "steady"
        if new_phase != phase:
            phase = new_phase
            print(
                f"[sim] Phase transition → steady-state "
                f"(elapsed={elapsed/3600:.1f}h, interval now {steady_interval}s)"
            )

        loop_num += 1
        interval = warmup_interval if phase == "warmup" else steady_interval

        client = redis.from_url(settings.redis_url, decode_responses=True)
        try:
            pushed = await _push_trip_batch(
                client,
                build_events,
                truck_count=truck_count,
                event_delay=event_delay,
                truck_delay=truck_delay,
            )
            print(
                f"[sim] Loop {loop_num} [{phase}]: pushed {pushed} packets "
                f"(next in {interval}s)"
            )
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
        help="Run continuously with adaptive rate control (warmup then steady-state).",
    )
    parser.add_argument(
        "--event-delay",
        type=float,
        default=2.0,
        help="Seconds between individual events within a truck (default: 2.0).",
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
        default=2,
        help="Number of trucks per batch (default: 2).",
    )
    parser.add_argument(
        "--warmup-interval",
        type=int,
        default=300,
        help="Seconds between batches during warmup phase (default: 300).",
    )
    parser.add_argument(
        "--steady-interval",
        type=int,
        default=3600,
        help="Seconds between batches after warmup (default: 3600).",
    )
    parser.add_argument(
        "--warmup-hours",
        type=float,
        default=2.0,
        help="Hours before switching to steady-state interval (default: 2.0).",
    )
    args = parser.parse_args()

    if args.loop:
        asyncio.run(
            _run_loop(
                event_delay=args.event_delay,
                truck_delay=args.truck_delay,
                truck_count=args.truck_count,
                warmup_interval=args.warmup_interval,
                steady_interval=args.steady_interval,
                warmup_hours=args.warmup_hours,
            )
        )
    else:
        asyncio.run(_run())


if __name__ == "__main__":
    main()
