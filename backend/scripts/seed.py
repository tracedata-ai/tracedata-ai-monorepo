"""
TraceData Backend — Database Seed Script.

Usage:
    python scripts/seed.py

This script populates the database with Singapore-relevant data for testing
multi-tenancy, IoT simulation, and agent routing.
"""

import asyncio
import logging
import uuid
from decimal import Decimal

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine
from app.models.base import Base
from app.models.tenant import Tenant
from app.models.driver import Driver
from app.models.fleet import Vehicle
from app.models.route import Route
from app.models.trip import Trip

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_data():
    """
    Seeds Singapore-relevant data partitioned by Tenant.
    """
    logger.info("🚀 Starting database seeding...")

    # ── 0. Create Tables (Dev mode) ───────────────────────────────────────────
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables verified/created.")

    async with AsyncSessionLocal() as session:
        try:
            # ── 1. Clean existing data (Nuke) ─────────────────────────────────
            # Order matters due to foreign key constraints if they existed, 
            # but we use CASCADE or SET NULL in models.
            logger.info("🧹 Cleaning existing data...")
            for table in [Trip, Route, Driver, Vehicle, Tenant]:
                await session.execute(delete(table))
            await session.commit()

            # ── 2. Create Tenants (Fleet Operators) ───────────────────────────
            logger.info("🏢 Creating Tenants...")
            t1 = Tenant(
                name="Singapore Logistics Hub",
                contact_email="ops@sg-logistics.com.sg",
                status="active"
            )
            t2 = Tenant(
                name="Tuas Haulage Solutions",
                contact_email="fleet@tuas-haulage.com",
                status="active"
            )
            session.add_all([t1, t2])
            await session.flush() # Populate IDs

            # ── 3. Create Drivers ─────────────────────────────────────────────
            logger.info("👨‍✈️ Creating Drivers...")
            # Tenant 1 Drivers
            d1 = Driver(
                tenant_id=t1.id,
                first_name="Wei Kiat",
                last_name="Tan",
                email="weikiat.tan@sg-logistics.com.sg",
                license_number="S1234567A",
                experience_level="expert"
            )
            d2 = Driver(
                tenant_id=t1.id,
                first_name="Siti",
                last_name="Aminah",
                email="siti.a@sg-logistics.com.sg",
                license_number="S7654321B",
                experience_level="intermediate"
            )
            # Tenant 2 Driver
            d3 = Driver(
                tenant_id=t2.id,
                first_name="Muthu",
                last_name="Kumaran",
                email="muthu.k@tuas-haulage.com",
                license_number="S9876543C",
                experience_level="novice"
            )
            session.add_all([d1, d2, d3])

            # ── 4. Create Vehicles ────────────────────────────────────────────
            logger.info("🚛 Creating Vehicles...")
            v1 = Vehicle(
                tenant_id=t1.id,
                license_plate="SBA 1234 A",
                make="Isuzu",
                model="N-Series (ELF)",
                year=2022,
                status="active"
            )
            v2 = Vehicle(
                tenant_id=t1.id,
                license_plate="SGE 5678 B",
                make="Mitsubishi Fuso",
                model="Canter",
                year=2021,
                status="active"
            )
            v3 = Vehicle(
                tenant_id=t2.id,
                license_plate="SMB 9101 C",
                make="Hino",
                model="300 Series",
                year=2023,
                status="active"
            )
            session.add_all([v1, v2, v3])
            await session.flush()

            # Assign vehicles to drivers (Optional)
            d1.vehicle_id = v1.id
            d3.vehicle_id = v3.id

            # ── 5. Create Routes ─────────────────────────────────────────────
            logger.info("📍 Creating Routes...")
            r1 = Route(
                tenant_id=t1.id,
                name="West-East Corridor",
                start_location="Tuas Logistic Hub",
                end_location="Changi Airfreight Centre",
                distance_km=Decimal("45.5"),
                route_type="highway"
            )
            r2 = Route(
                tenant_id=t2.id,
                name="Northern Loop",
                start_location="Woodlands Industrial Park",
                end_location="Jurong Port",
                distance_km=Decimal("28.2"),
                route_type="mixed"
            )
            session.add_all([r1, r2])
            await session.flush()

            # ── 6. Create Initial Trips ───────────────────────────────────────
            logger.info("🛣️  Creating Trips...")
            # Active trip for T1
            trip1 = Trip(
                tenant_id=t1.id,
                driver_id=d1.id,
                vehicle_id=v1.id,
                route_id=r1.id,
                status="active"
            )
            # Completed trip for T1
            trip2 = Trip(
                tenant_id=t1.id,
                driver_id=d2.id,
                vehicle_id=v2.id,
                route_id=r1.id,
                status="completed",
                safety_score=Decimal("88.5"),
                score_explanation="Clean trip with minor idling at Changi."
            )
            # Active trip for T2
            trip3 = Trip(
                tenant_id=t2.id,
                driver_id=d3.id,
                vehicle_id=v3.id,
                route_id=r2.id,
                status="active"
            )
            session.add_all([trip1, trip2, trip3])
            await session.flush()  # Ensure IDs are generated for foreign keys

            # ── 7. Create Issues ─────────────────────────────────────────────
            logger.info("⚠️  Creating Issues...")
            from app.models.issue import Issue
            i1 = Issue(
                tenant_id=t1.id,
                trip_id=trip1.id,
                event_type="harsh_brake",
                category="harsh_events",
                severity="medium",
                description="Harsh braking detected near Tuas Viaduct."
            )
            i2 = Issue(
                tenant_id=t1.id,
                trip_id=trip2.id,
                event_type="speeding",
                category="speed_compliance",
                severity="high",
                description="Exceeded 70km/h on Changi Coast Rd."
            )
            session.add_all([i1, i2])

            await session.commit()
            logger.info("✅ Seeding complete!")

        except Exception as e:
            logger.error(f"❌ Seeding failed: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(seed_data())
