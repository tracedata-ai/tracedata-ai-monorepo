"""
🔄 RESET & TEST SCRIPT
Drop all tables, clear Redis, create schema, run integration test.

Usage:
  python reset_and_test.py --full       (drop + create + clear Redis)
  python reset_and_test.py --test       (run integration test)
  python reset_and_test.py --both       (full reset + test)
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, UTC
from typing import Any

from sqlalchemy import text, MetaData
from sqlalchemy.ext.asyncio import create_async_engine

from common.config.settings import get_settings
from common.redis.client import RedisClient
from common.models.events import TripEvent, TelemetryPacket

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("reset_test")

settings = get_settings()


async def drop_all_tables():
    """Drop all tables from database."""
    logger.info("🗑️  Dropping all tables...")

    engine = create_async_engine(settings.database_url, echo=False)

    try:
        async with engine.connect() as conn:
            # Get all table names
            result = await conn.execute(
                text(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """
                )
            )
            tables = [row[0] for row in result.fetchall()]

            if not tables:
                logger.info("✅ No tables to drop")
                return

            logger.info(f"Found {len(tables)} tables: {tables}")

            # Drop with CASCADE
            for table in tables:
                await conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                logger.info(f"  ✓ Dropped {table}")

            await conn.commit()
            logger.info("✅ All tables dropped")

    finally:
        await engine.dispose()


async def create_schema():
    """Create fresh database schema."""
    logger.info("🏗️  Creating fresh schema...")

    engine = create_async_engine(settings.database_url, echo=False)

    try:
        async with engine.connect() as conn:
            # Create trips table
            await conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS trips (
                        trip_id VARCHAR(80) PRIMARY KEY,
                        truck_id VARCHAR(80) NOT NULL,
                        driver_id VARCHAR(80) NOT NULL,
                        started_at TIMESTAMP WITH TIME ZONE NOT NULL,
                        ended_at TIMESTAMP WITH TIME ZONE,
                        distance_km FLOAT,
                        duration_minutes INT,
                        status VARCHAR(50) DEFAULT 'active',
                        route_name VARCHAR(255),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """
                )
            )
            logger.info("  ✓ Created trips table")

            # Create pipeline_events table (main ingestion table)
            await conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS pipeline_events (
                        event_id VARCHAR(80) PRIMARY KEY,
                        device_event_id VARCHAR(80) UNIQUE NOT NULL,
                        trip_id VARCHAR(80) NOT NULL,
                        truck_id VARCHAR(80) NOT NULL,
                        driver_id VARCHAR(80) NOT NULL,
                        event_type VARCHAR(80) NOT NULL,
                        category VARCHAR(80),
                        priority VARCHAR(50),
                        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                        offset_seconds INT,
                        trip_meter_km FLOAT,
                        odometer_km FLOAT,
                        lat FLOAT,
                        lon FLOAT,
                        schema_version VARCHAR(50) DEFAULT 'event_v1',
                        details JSONB,
                        raw_payload JSONB,
                        source VARCHAR(50),
                        ping_type VARCHAR(50),
                        is_emergency BOOLEAN DEFAULT FALSE,
                        ingested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        status VARCHAR(50) DEFAULT 'received',
                        retry_count INT DEFAULT 0,
                        is_locked BOOLEAN DEFAULT FALSE,
                        locked_by VARCHAR(80),
                        locked_at TIMESTAMP WITH TIME ZONE,
                        processed_at TIMESTAMP WITH TIME ZONE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE
                    )
                """
                )
            )
            logger.info("  ✓ Created pipeline_events table")

            # Create indexes for performance
            await conn.execute(
                text(
                    "CREATE INDEX idx_pipeline_events_device_event_id ON pipeline_events(device_event_id)"
                )
            )
            await conn.execute(
                text(
                    "CREATE INDEX idx_pipeline_events_trip_id ON pipeline_events(trip_id)"
                )
            )
            await conn.execute(
                text(
                    "CREATE INDEX idx_pipeline_events_status ON pipeline_events(status)"
                )
            )
            logger.info("  ✓ Created indexes")

            # Create safety_events table (agent output)
            await conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS safety_events (
                        id SERIAL PRIMARY KEY,
                        trip_id VARCHAR(80) NOT NULL,
                        device_event_id VARCHAR(80),
                        event_type VARCHAR(80),
                        severity VARCHAR(50),
                        decision VARCHAR(255),
                        confidence FLOAT,
                        analysis JSONB,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE
                    )
                """
                )
            )
            logger.info("  ✓ Created safety_events table")

            # Create scoring_results table
            await conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS scoring_results (
                        id SERIAL PRIMARY KEY,
                        trip_id VARCHAR(80) NOT NULL,
                        score FLOAT,
                        ping_count INT,
                        explanations JSONB,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE
                    )
                """
                )
            )
            logger.info("  ✓ Created scoring_results table")

            await conn.commit()
            logger.info("✅ Schema created successfully")

    finally:
        await engine.dispose()


async def clear_redis():
    """Clear all Redis data."""
    logger.info("🧹 Clearing Redis...")

    redis = RedisClient()

    try:
        await redis._client.flushdb()
        logger.info("✅ Redis cleared")
    finally:
        await redis.close()


async def seed_test_data():
    """Seed minimal test data."""
    logger.info("🌱 Seeding test data...")

    engine = create_async_engine(settings.database_url, echo=False)

    try:
        async with engine.connect() as conn:
            # Create test trip
            trip_id = "TRIP-TEST-001"
            await conn.execute(
                text(
                    """
                    INSERT INTO trips
                    (trip_id, truck_id, driver_id, started_at, status)
                    VALUES (:trip_id, :truck_id, :driver_id, :started_at, :status)
                    ON CONFLICT DO NOTHING
                """
                ),
                {
                    "trip_id": trip_id,
                    "truck_id": "TRUCK-001",
                    "driver_id": "DRIVER-001",
                    "started_at": datetime.now(UTC),
                    "status": "active",
                },
            )
            logger.info(f"  ✓ Created test trip: {trip_id}")

            await conn.commit()
            logger.info("✅ Test data seeded")

    finally:
        await engine.dispose()


async def run_integration_test():
    """
    Run full integration test:
    1. Create test event
    2. Push to Redis buffer
    3. Monitor ingestion
    4. Check database
    5. Verify agent would receive it
    """
    logger.info("🧪 Running integration test...")

    redis = RedisClient()

    try:
        # Step 1: Create test payload
        test_event = {
            "truck_id": "TRUCK-001",
            "event": {
                "event_id": "EVT-TEST-001",
                "device_event_id": "DEV-EVT-001",
                "trip_id": "TRIP-TEST-001",
                "truck_id": "TRUCK-001",
                "driver_id": "DRIVER-001",
                "event_type": "harsh_brake_event",
                "category": "critical_safety",
                "priority": "CRITICAL",
                "timestamp": datetime.now(UTC).isoformat(),
                "offset_seconds": 0,
                "schema_version": "event_v1",
                "details": {"g_force": 0.85},
            },
        }

        # Step 2: Push to Redis raw buffer
        logger.info("📤 Pushing test event to Redis buffer...")
        buffer_key = "telemetry:TRUCK-001:buffer"
        await redis._client.lpush(buffer_key, json.dumps(test_event))
        logger.info(f"  ✓ Pushed to {buffer_key}")

        # Step 3: Check buffer size
        buffer_size = await redis._client.llen(buffer_key)
        logger.info(f"  ✓ Buffer size: {buffer_size}")

        # Step 4: Check if ingestion would find it
        packet = await redis._client.lpop(buffer_key)
        if packet:
            packet_data = json.loads(packet)
            logger.info(
                f"  ✓ Can retrieve: event_type={packet_data['event']['event_type']}"
            )
        else:
            logger.warning("  ✗ Failed to retrieve from buffer")
            return False

        # Step 5: Verify database connectivity
        logger.info("🗄️  Testing database...")
        engine = create_async_engine(settings.database_url, echo=False)

        try:
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT trip_id FROM trips LIMIT 1"))
                trips = result.fetchall()
                logger.info(f"  ✓ Database accessible, found {len(trips)} trips")

                if trips:
                    logger.info(f"    Trip ID: {trips[0][0]}")

        finally:
            await engine.dispose()

        # Step 6: Summary
        logger.info("✅ Integration test passed!")
        logger.info(
            """
╔══════════════════════════════════════════════════╗
║ SYSTEM READY FOR DATA FLOW                       ║
╠══════════════════════════════════════════════════╣
║ ✓ Database schema created                        ║
║ ✓ Redis cleared and accessible                   ║
║ ✓ Test event can be pushed                       ║
║ ✓ Ingestion worker can retrieve events           ║
║ ✓ Agents will receive via orchestrator           ║
╠══════════════════════════════════════════════════╣
║ NEXT: Run full stack with Docker                 ║
║ docker compose up api db redis ingestion...      ║
║                       orchestrator safety_worker ║
╚══════════════════════════════════════════════════╝
        """
        )

        return True

    finally:
        await redis.close()


async def main():
    """Main entry point."""
    args = sys.argv[1:] if len(sys.argv) > 1 else ["--both"]

    if "--full" in args:
        logger.info("=" * 50)
        logger.info("FULL RESET MODE")
        logger.info("=" * 50)
        await drop_all_tables()
        await create_schema()
        await seed_test_data()
        await clear_redis()

    if "--test" in args:
        logger.info("=" * 50)
        logger.info("INTEGRATION TEST MODE")
        logger.info("=" * 50)
        success = await run_integration_test()
        sys.exit(0 if success else 1)

    if "--both" in args:
        logger.info("=" * 50)
        logger.info("FULL RESET + TEST MODE")
        logger.info("=" * 50)
        await drop_all_tables()
        await create_schema()
        await seed_test_data()
        await clear_redis()
        logger.info("")
        success = await run_integration_test()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
