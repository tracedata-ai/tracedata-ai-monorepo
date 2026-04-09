"""
Idempotent Singapore baseline bootstrap for local Docker runs.

Creates baseline entities:
- 1 tenant
- 10 drivers
- 10 trucks
- 20 routes

And pushes one baseline trip workflow per truck to Redis buffer:
start -> 3 harsh -> 12-18 smooth (default 15) -> end -> feedback
"""

from __future__ import annotations

import argparse
import importlib
import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import redis.asyncio as redis
from sqlalchemy import select, text

from api.models.driver import Driver
from api.models.fleet import Vehicle
from api.models.route import Route
from api.models.tenant import Tenant
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


async def _ensure_baseline_entities() -> tuple[list[Driver], list[Vehicle]]:
    async with AsyncSessionLocal() as session:
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

        # Ensure 10 drivers
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

        # Ensure 10 vehicles/trucks
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

        # Ensure 20 Singapore routes
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
        return drivers[:10], vehicles[:10]


async def _push_baseline_trip_packets(*, smooth_count: int) -> int:
    settings = get_settings()
    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        if await client.get(BOOTSTRAP_MARKER_KEY):
            return 0

        fixture_mod = importlib.import_module(
            "common.workflow_fixtures.sg_baseline_trip"
        )
        build_events = fixture_mod.build_events

        await _ensure_baseline_entities()
        now = datetime.now(UTC).replace(microsecond=0)
        total_pushed = 0

        for idx in range(10):
            trip_id = f"TRP-SG-BASE-{idx+1:02d}"
            truck_id = f"TK{idx+1:03d}"
            driver_id = f"DRV-SG-{idx+1:03d}"

            # Stagger starts by 2 minutes to avoid identical timestamps.
            anchor = now + timedelta(minutes=idx * 2)
            packets = build_events(
                trip_id=trip_id,
                truck_id=truck_id,
                driver_id=driver_id,
                anchor=anchor,
                smooth_count=smooth_count,
            )
            key = f"telemetry:{truck_id}:buffer"
            for score, packet in enumerate(packets):
                await client.zadd(key, {json.dumps(packet): score})
                total_pushed += 1

        await client.set(BOOTSTRAP_MARKER_KEY, "ok")
        return total_pushed
    finally:
        await client.aclose()


async def _run(smooth_count: int) -> None:
    # Ensure tables exist when running before FastAPI lifespan startup.
    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS scoring_schema"))
        await conn.run_sync(Base.metadata.create_all)

    await _ensure_baseline_entities()
    pushed = await _push_baseline_trip_packets(smooth_count=smooth_count)
    if pushed:
        print(f"Bootstrap complete: pushed {pushed} telemetry packets.")
    else:
        print("Bootstrap skipped: marker already present.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bootstrap SG baseline entities and events."
    )
    parser.add_argument(
        "--smooth-count",
        type=int,
        default=15,
        help="Number of 10-minute smoothness windows per trip (12-18).",
    )
    args = parser.parse_args()
    import asyncio

    asyncio.run(_run(args.smooth_count))


if __name__ == "__main__":
    main()
