"""
TraceData Backend — Database Seed Script.

Usage:
    python scripts/seed.py

This script populates the database with Singapore-relevant data for testing
multi-tenancy, IoT simulation, and agent routing.
"""

import asyncio
from decimal import Decimal

from sqlalchemy import delete

from api.models.base import Base as ApiBase
from api.models.driver import Driver
from api.models.fleet import Vehicle
from api.models.route import Route
from api.models.tenant import Tenant
from api.models.trip import Trip
from common.db.engine import AsyncSessionLocal, engine
from common.models.orm import Base as PipelineBase
from core.logging import LogToken, get_logger, setup_logging

# Module-level logger — uses the script's path (scripts.seed) as the logger name
logger = get_logger(__name__)


SEED_DATA = {
    "tenants": [
        {
            "key": "t1",
            "name": "Singapore Logistics Hub",
            "contact_email": "ops@sg-logistics.com.sg",
            "status": "active",
        },
        {
            "key": "t2",
            "name": "Tuas Haulage Solutions",
            "contact_email": "fleet@tuas-haulage.com",
            "status": "active",
        },
    ],
    "drivers": [
        {
            "key": "d1",
            "tenant": "t1",
            "first_name": "Wei Kiat",
            "last_name": "Tan",
            "email": "weikiat.tan@sg-logistics.com.sg",
            "license_number": "S1234567A",
            "experience_level": "expert",
        },
        {
            "key": "d2",
            "tenant": "t1",
            "first_name": "Siti",
            "last_name": "Aminah",
            "email": "siti.a@sg-logistics.com.sg",
            "license_number": "S7654321B",
            "experience_level": "intermediate",
        },
        {
            "key": "d3",
            "tenant": "t2",
            "first_name": "Muthu",
            "last_name": "Kumaran",
            "email": "muthu.k@tuas-haulage.com",
            "license_number": "S9876543C",
            "experience_level": "novice",
        },
    ],
    "vehicles": [
        {
            "key": "v1",
            "tenant": "t1",
            "license_plate": "SBA 1234 A",
            "make": "Isuzu",
            "model": "N-Series (ELF)",
            "year": 2022,
            "status": "active",
        },
        {
            "key": "v2",
            "tenant": "t1",
            "license_plate": "SGE 5678 B",
            "make": "Mitsubishi Fuso",
            "model": "Canter",
            "year": 2021,
            "status": "active",
        },
        {
            "key": "v3",
            "tenant": "t2",
            "license_plate": "SMB 9101 C",
            "make": "Hino",
            "model": "300 Series",
            "year": 2023,
            "status": "active",
        },
    ],
    "driver_vehicle_assignments": [
        {"driver": "d1", "vehicle": "v1"},
        {"driver": "d3", "vehicle": "v3"},
    ],
    "routes": [
        {
            "key": "r1",
            "tenant": "t1",
            "name": "West-East Corridor",
            "start_location": "Tuas Logistic Hub",
            "end_location": "Changi Airfreight Centre",
            "distance_km": Decimal("45.5"),
            "route_type": "highway",
        },
        {
            "key": "r2",
            "tenant": "t2",
            "name": "Northern Loop",
            "start_location": "Woodlands Industrial Park",
            "end_location": "Jurong Port",
            "distance_km": Decimal("28.2"),
            "route_type": "mixed",
        },
    ],
    "trips": [
        {
            "key": "trip1",
            "tenant": "t1",
            "driver": "d1",
            "vehicle": "v1",
            "route": "r1",
            "status": "active",
        },
        {
            "key": "trip2",
            "tenant": "t1",
            "driver": "d2",
            "vehicle": "v2",
            "route": "r1",
            "status": "completed",
            "safety_score": Decimal("88.5"),
            "score_explanation": "Clean trip with minor idling at Changi.",
        },
        {
            "key": "trip3",
            "tenant": "t2",
            "driver": "d3",
            "vehicle": "v3",
            "route": "r2",
            "status": "active",
        },
    ],
    "issues": [
        {
            "tenant": "t1",
            "trip": "trip1",
            "event_type": "harsh_brake",
            "category": "harsh_events",
            "severity": "medium",
            "description": "Harsh braking detected near Tuas Viaduct.",
        },
        {
            "tenant": "t1",
            "trip": "trip2",
            "event_type": "speeding",
            "category": "speed_compliance",
            "severity": "high",
            "description": "Exceeded 70km/h on Changi Coast Rd.",
        },
    ],
}


async def seed_data():
    """
    Seeds Singapore-relevant data partitioned by Tenant.
    """
    setup_logging()  # Standardize output for this script
    logger.info(f"{LogToken.SEED_START} Starting database seeding...")

    # ── 0. Create Tables (Dev mode) ───────────────────────────────────────────
    # Create both API tables and pipeline tables in order (foreign key dependencies)
    async with engine.begin() as conn:
        await conn.run_sync(
            ApiBase.metadata.create_all
        )  # Tenants, drivers, vehicles, routes first
        await conn.run_sync(PipelineBase.metadata.create_all)  # Events, trips second
    logger.info(f"{LogToken.DATABASE_INIT} API and pipeline tables verified/created.")

    async with AsyncSessionLocal() as session:
        try:
            # ── 1. Clean existing data (Nuke) ─────────────────────────────────
            # Order matters due to foreign key constraints if they existed,
            # but we use CASCADE or SET NULL in models.
            logger.info(f"{LogToken.DATABASE} Cleaning existing data...")
            for table in [Trip, Route, Driver, Vehicle, Tenant]:
                await session.execute(delete(table))
            await session.commit()

            # ── 2. Create Tenants (Fleet Operators) ───────────────────────────
            logger.info(f"{LogToken.SEED} Creating Tenants...")
            tenants_by_key: dict[str, Tenant] = {}
            for row in SEED_DATA["tenants"]:
                tenant = Tenant(
                    name=row["name"],
                    contact_email=row["contact_email"],
                    status=row["status"],
                )
                tenants_by_key[row["key"]] = tenant
                session.add(tenant)
            await session.flush()  # Populate IDs for tenant references

            # ── 3. Create Drivers ─────────────────────────────────────────────
            logger.info(f"{LogToken.SEED} Creating Drivers...")
            drivers_by_key: dict[str, Driver] = {}
            for row in SEED_DATA["drivers"]:
                driver = Driver(
                    tenant_id=tenants_by_key[row["tenant"]].id,
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    email=row["email"],
                    license_number=row["license_number"],
                    experience_level=row["experience_level"],
                )
                drivers_by_key[row["key"]] = driver
                session.add(driver)

            # ── 4. Create Vehicles ────────────────────────────────────────────
            logger.info(f"{LogToken.SEED} Creating Vehicles...")
            vehicles_by_key: dict[str, Vehicle] = {}
            for row in SEED_DATA["vehicles"]:
                vehicle = Vehicle(
                    tenant_id=tenants_by_key[row["tenant"]].id,
                    license_plate=row["license_plate"],
                    make=row["make"],
                    model=row["model"],
                    year=row["year"],
                    status=row["status"],
                )
                vehicles_by_key[row["key"]] = vehicle
                session.add(vehicle)

            await session.flush()  # Populate IDs used by optional assignments and trips

            # Assign vehicles to drivers (optional)
            for row in SEED_DATA["driver_vehicle_assignments"]:
                drivers_by_key[row["driver"]].vehicle_id = vehicles_by_key[
                    row["vehicle"]
                ].id

            # ── 5. Create Routes ─────────────────────────────────────────────
            logger.info(f"{LogToken.SEED} Creating Routes...")
            routes_by_key: dict[str, Route] = {}
            for row in SEED_DATA["routes"]:
                route = Route(
                    tenant_id=tenants_by_key[row["tenant"]].id,
                    name=row["name"],
                    start_location=row["start_location"],
                    end_location=row["end_location"],
                    distance_km=row["distance_km"],
                    route_type=row["route_type"],
                )
                routes_by_key[row["key"]] = route
                session.add(route)
            await session.flush()

            # ── 6. Create Initial Trips ───────────────────────────────────────
            logger.info(f"{LogToken.SEED} Creating Trips...")
            trips_by_key: dict[str, Trip] = {}
            for row in SEED_DATA["trips"]:
                trip = Trip(
                    tenant_id=tenants_by_key[row["tenant"]].id,
                    driver_id=drivers_by_key[row["driver"]].id,
                    vehicle_id=vehicles_by_key[row["vehicle"]].id,
                    route_id=routes_by_key[row["route"]].id,
                    status=row["status"],
                    safety_score=row.get("safety_score"),
                    score_explanation=row.get("score_explanation"),
                )
                trips_by_key[row["key"]] = trip
                session.add(trip)
            await session.flush()  # Ensure IDs are generated for issue foreign keys

            # ── 7. Create Issues ─────────────────────────────────────────────
            logger.info(f"{LogToken.SEED} Creating Issues...")
            from api.models.issue import Issue

            for row in SEED_DATA["issues"]:
                issue = Issue(
                    tenant_id=tenants_by_key[row["tenant"]].id,
                    trip_id=trips_by_key[row["trip"]].id,
                    event_type=row["event_type"],
                    category=row["category"],
                    severity=row["severity"],
                    description=row["description"],
                )
                session.add(issue)

            await session.commit()
            logger.info(f"{LogToken.SEED_SUCCESS} Seeding complete!")

        except Exception as e:
            logger.error(f"{LogToken.SEED_FAIL} Seeding failed: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_data())
