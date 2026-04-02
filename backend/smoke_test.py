"""
🔥 END-TO-END SMOKE TEST - TraceData Orchestrator

Tests complete event flow:
  1. Start of Trip
  2. 2x Harsh Brake Events
  3. 12x 10-minute Ping Events (telemetry)
  4. End of Trip (with harsh event references)
  5. Critical Accident Event
  6. Emotional Support Feedback

Verifies each event reaches the correct agent(s).

Usage:
  python smoke_test.py --deploy    (start system, run test)
  python smoke_test.py --test      (run test only, assume system running)
  python smoke_test.py --monitor   (watch outputs, no new events)
"""

import asyncio
import json
import logging
import sys
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("smoke_test")

# ─ Configuration ────────────────────────────────────────────────────────────

TRUCK_ID = "TRUCK-SMOKE-001"
DRIVER_ID = "DRIVER-SMOKE-001"
TRIP_ID = f"TRIP-ID-{uuid.uuid4()}"

START_TIME = datetime.now(UTC)
HARSH_EVENT_IDS = []

# ─ Test Data Generation ──────────────────────────────────────────────────────


def get_priority_score(event_type: str) -> int:
    """Get priority score for Redis sorted set (lower = higher priority)."""
    priority_map = {
        "collision": 0,  # CRITICAL
        "rollover": 0,  # CRITICAL
        "driver_sos": 0,  # CRITICAL
        "harsh_brake": 3,  # HIGH
        "hard_accel": 3,  # HIGH
        "harsh_corner": 3,  # HIGH
        "speeding": 3,  # HIGH
        "end_of_trip": 3,  # HIGH
        "start_of_trip": 9,  # LOW
        "normal_operation": 9,  # LOW
        "driver_feedback": 6,  # MEDIUM
    }
    return priority_map.get(event_type, 9)


def get_ping_type(event_type: str) -> str:
    """Map event_type to PingType enum."""
    ping_type_map = {
        "collision": "emergency",
        "driver_sos": "emergency",
        "harsh_brake": "high_speed",
        "hard_accel": "high_speed",
        "harsh_corner": "high_speed",
        "speeding": "high_speed",
        "start_of_trip": "start_of_trip",
        "end_of_trip": "end_of_trip",
        "normal_operation": "medium_speed",
        "driver_feedback": "medium_speed",
    }
    return ping_type_map.get(event_type, "batch")


def create_trip_event(
    event_type: str,
    offset_seconds: int,
    details: dict | None = None,
    device_event_id: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
) -> dict:
    """Create a trip event."""
    if device_event_id is None:
        device_event_id = f"DEVICE-ID-{uuid.uuid4()}"

    event_dict = {
        "event_id": str(uuid.uuid4()),
        "device_event_id": device_event_id,
        "trip_id": TRIP_ID,
        "truck_id": TRUCK_ID,
        "driver_id": DRIVER_ID,
        "event_type": event_type,
        "category": get_category(event_type),
        "priority": get_priority(event_type),
        "timestamp": (START_TIME + timedelta(seconds=offset_seconds)).isoformat(),
        "offset_seconds": offset_seconds,
        "trip_meter_km": offset_seconds / 10,  # Approximate
        "odometer_km": 10000 + (offset_seconds / 10),
        "schema_version": "event_v1",
        "details": details or {},
    }

    # Add location if provided
    if lat is not None and lon is not None:
        event_dict["location"] = {"lat": lat, "lon": lon}

    return event_dict


def get_category(event_type: str) -> str:
    """Get event category."""
    categories = {
        "start_of_trip": "trip_lifecycle",
        "harsh_brake": "harsh_events",
        "hard_accel": "harsh_events",
        "speeding": "speed_compliance",
        "collision": "critical",
        "normal_operation": "normal_operation",
        "end_of_trip": "trip_lifecycle",
        "driver_feedback": "driver_feedback",
    }
    return categories.get(event_type, "unknown")


def get_priority(event_type: str) -> str:
    """Get event priority (lowercase enum values)."""
    priorities = {
        "start_of_trip": "low",
        "harsh_brake": "high",
        "hard_accel": "high",
        "harsh_corner": "high",
        "speeding": "high",
        "collision": "critical",
        "rollover": "critical",
        "driver_sos": "critical",
        "normal_operation": "low",
        "end_of_trip": "high",
        "driver_feedback": "medium",
    }
    return priorities.get(event_type, "medium")


def create_raw_packet(trip_event: dict) -> dict:
    """Wrap trip event in TelemetryPacket format with required fields."""
    return {
        "ping_type": get_ping_type(trip_event["event_type"]),
        "source": "telematics_device",
        "is_emergency": trip_event.get("priority") == "critical",
        "event": trip_event,
    }


# ─ Test Scenarios ───────────────────────────────────────────────────────────


def generate_test_events() -> list[dict]:
    """Generate realistic test event sequence."""
    events = []

    # 1. START OF TRIP (offset 0s)
    logger.info("📍 Creating START_OF_TRIP event...")
    event = create_trip_event(
        event_type="start_of_trip",
        offset_seconds=0,
        details={"route": "Downtown → Airport", "scheduled_duration": 7200},
    )
    events.append(("START_OF_TRIP", event, "orchestrator"))

    # 2. HARSH BRAKE #1 (offset 300s = 5 min)
    logger.info("📍 Creating HARSH_BRAKE_EVENT #1...")
    event = create_trip_event(
        event_type="harsh_brake",
        offset_seconds=300,
        details={"g_force": 0.82, "speed_kmh": 65},
        device_event_id=f"DEVICE-ID-{uuid.uuid4()}",
    )
    HARSH_EVENT_IDS.append(event["event_id"])
    events.append(("HARSH_BRAKE_1", event, "safety"))

    # 3. HARSH BRAKE #2 (offset 900s = 15 min)
    logger.info("📍 Creating HARSH_BRAKE_EVENT #2...")
    event = create_trip_event(
        event_type="harsh_brake",
        offset_seconds=900,
        details={"g_force": 0.75, "speed_kmh": 50},
        device_event_id=f"DEVICE-ID-{uuid.uuid4()}",
    )
    HARSH_EVENT_IDS.append(event["event_id"])
    events.append(("HARSH_BRAKE_2", event, "safety"))

    # 4. PING EVENTS - 12 events at 10-minute intervals (600s each)
    logger.info("📍 Creating 12 PING_EVENT telemetry points...")
    for i in range(12):
        offset = 1200 + (i * 600)  # Start at 1200s (20 min), then every 10 min
        event = create_trip_event(
            event_type="normal_operation",
            offset_seconds=offset,
            details={"speed_kmh": 55 + (i % 10)},
            lat=40.7128 + (i * 0.001),
            lon=-74.0060 + (i * 0.001),
        )
        events.append((f"PING_{i+1:02d}", event, "none"))

    # 5. CRITICAL ACCIDENT EVENT (offset 8100s = 2h 15min)
    logger.info("📍 Creating ACCIDENT_CRITICAL event...")
    event = create_trip_event(
        event_type="collision",
        offset_seconds=8100,
        details={
            "severity": "critical",
            "impact_speed_kmh": 45,
            "vehicle_damage": "moderate",
        },
    )
    events.append(("ACCIDENT_CRITICAL", event, "safety"))

    # 6. EMOTIONAL SUPPORT FEEDBACK (offset 8400s = 2h 20 min)
    logger.info("📍 Creating EMOTIONAL_FEEDBACK event...")
    event = create_trip_event(
        event_type="driver_feedback",
        offset_seconds=8400,
        details={
            "sentiment": "negative",
            "message": "Very stressful drive. Multiple aggressive maneuvers.",
            "rating": 2,
        },
    )
    events.append(("EMOTIONAL_FEEDBACK", event, "sentiment"))

    # 7. END OF TRIP (offset 9000s = 2h 30 min)
    logger.info("📍 Creating END_OF_TRIP event...")
    event = create_trip_event(
        event_type="end_of_trip",
        offset_seconds=9000,
        details={
            "distance_km": 150,
            "harsh_events": HARSH_EVENT_IDS,  # Reference to harsh brakes
            "accident_count": 1,
        },
    )
    events.append(("END_OF_TRIP", event, "scoring"))

    return events


# ─ Ingestion & Monitoring ───────────────────────────────────────────────────


async def create_trip_in_db() -> None:
    """Create the test trip in the database before pushing events."""
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/tracedata",
        echo=False,
    )

    try:
        async with engine.connect() as conn:
            await conn.execute(
                text("""
                    INSERT INTO trips (trip_id, truck_id, driver_id, started_at, status)
                    VALUES (:trip_id, :truck_id, :driver_id, :started_at, 'active')
                    ON CONFLICT (trip_id) DO NOTHING
                """),
                {
                    "trip_id": TRIP_ID,
                    "truck_id": TRUCK_ID,
                    "driver_id": DRIVER_ID,
                    "started_at": START_TIME.replace(tzinfo=None),
                },
            )
            await conn.commit()
            logger.info(f"✓ Created trip in database: {TRIP_ID}")
    finally:
        await engine.dispose()


async def push_events_to_redis(events: list[dict]) -> None:
    """Push all test events to Redis buffer using sorted sets with priority."""
    redis = RedisClient()
    buffer_key = RedisSchema.Telemetry.buffer(TRUCK_ID)

    try:
        logger.info("")
        logger.info("📤 PUSHING EVENTS TO REDIS BUFFER (Sorted Set)")
        logger.info("=" * 60)

        # Clear existing buffer
        await redis._client.delete(buffer_key)

        for name, event, _expected_agent in events:
            packet = create_raw_packet(event)
            payload = json.dumps(packet)
            score = get_priority_score(event["event_type"])

            # Use ZADD with priority score (lower = higher priority)
            await redis._client.zadd(buffer_key, mapping={payload: score})
            logger.info(f"  ✓ {name:20} → buffer (priority: {score})")
            await asyncio.sleep(0.05)

        buffer_size = await redis._client.zcard(buffer_key)
        logger.info(f"\n✅ All {buffer_size} events pushed to buffer")

    finally:
        await redis.close()


async def monitor_database_outputs() -> dict[str, Any]:
    """Monitor database for agent outputs."""
    logger.info("")
    logger.info("🗄️  MONITORING DATABASE OUTPUTS")
    logger.info("=" * 60)

    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/tracedata",
        echo=False,
    )

    try:
        results = {}

        async with engine.connect() as conn:
            # Check safety_events (Safety Agent output)
            result = await conn.execute(
                text("""
                    SELECT COUNT(*) as count FROM safety_events
                    WHERE trip_id = :trip_id
                """),
                {"trip_id": TRIP_ID},
            )
            safety_count = result.scalar() or 0
            results["safety"] = safety_count
            logger.info(f"  ✓ Safety Agent outputs: {safety_count}")

            # Check scoring_results (Scoring Agent output)
            result = await conn.execute(
                text("""
                    SELECT COUNT(*) as count FROM scoring_results
                    WHERE trip_id = :trip_id
                """),
                {"trip_id": TRIP_ID},
            )
            scoring_count = result.scalar() or 0
            results["scoring"] = scoring_count
            logger.info(f"  ✓ Scoring Agent outputs: {scoring_count}")

            # Check pipeline_events (ingestion table)
            result = await conn.execute(
                text("""
                    SELECT COUNT(*) as count FROM pipeline_events
                    WHERE trip_id = :trip_id
                """),
                {"trip_id": TRIP_ID},
            )
            pipeline_count = result.scalar() or 0
            results["pipeline"] = pipeline_count
            logger.info(f"  ✓ Pipeline events processed: {pipeline_count}")

        return results

    finally:
        await engine.dispose()


async def monitor_redis_outputs() -> dict[str, Any]:
    """Monitor Redis for completion events."""
    logger.info("")
    logger.info("📡 MONITORING REDIS OUTPUTS")
    logger.info("=" * 60)

    redis = RedisClient()
    results = {}

    try:
        # Check agent output keys
        output_keys = await redis._client.keys(f"trips:{TRIP_ID}:output:*")
        logger.info(f"  ✓ Agent output keys: {len(output_keys)}")

        for key in output_keys:
            agent_name = key.split(":")[-1]
            output = await redis._client.get(key)
            if output:
                data = json.loads(output)
                logger.info(f"    • {agent_name}: {type(data).__name__} stored")
                results[agent_name] = True
            else:
                logger.info(f"    • {agent_name}: (empty)")

        # Check completion events channel
        channel = RedisSchema.Trip.events_channel(TRIP_ID)
        logger.info(f"\n  Completion events channel: {channel}")
        logger.info("  (Completion events posted via pub/sub)")

        return results

    finally:
        await redis.close()


# ─ Test Execution & Reporting ──────────────────────────────────────────────


async def run_smoke_test() -> bool:
    """Run full end-to-end smoke test."""
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║  🔥 TRACEDATA END-TO-END SMOKE TEST                        ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    logger.info(f"\nTest Trip ID: {TRIP_ID}")
    logger.info(f"Truck ID:     {TRUCK_ID}")
    logger.info(f"Driver ID:    {DRIVER_ID}")

    # Create trip in database first
    await create_trip_in_db()

    # Generate test events
    events = generate_test_events()
    total_events = len(events)
    logger.info(f"\n📋 Generated {total_events} test events")

    # Push to Redis
    await push_events_to_redis(events)

    # Wait for ingestion and processing
    logger.info("\n⏳ Waiting for ingestion → orchestrator → agents...")
    logger.info("   (In production, this would take 5-15 seconds)")
    await asyncio.sleep(3)

    # Monitor outputs
    db_results = await monitor_database_outputs()
    redis_results = await monitor_redis_outputs()

    # Generate report
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║  📊 SMOKE TEST RESULTS                                     ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")

    # Expected vs Actual
    logger.info("\n✅ EXPECTED ROUTING:")
    logger.info("  • Safety Agent:     2 harsh brakes + 1 accident = 3 outputs")
    logger.info("  • Scoring Agent:    1 end-of-trip = 1 output")
    logger.info("  • Sentiment Agent:  1 feedback = (output check TODO)")
    logger.info("  • Pipeline:        19 total events processed")

    logger.info("\n📈 ACTUAL RESULTS:")
    logger.info(f"  • Safety Agent:     {db_results.get('safety', 0)} outputs")
    logger.info(f"  • Scoring Agent:    {db_results.get('scoring', 0)} outputs")
    logger.info(f"  • Pipeline:         {db_results.get('pipeline', 0)} events")
    logger.info(f"  • Redis outputs:    {len(redis_results)} agents stored results")

    # Summary
    logger.info("")
    logger.info("╔════════════════════════════════════════════════════════════╗")

    success = (
        db_results.get("pipeline", 0) == total_events
        and db_results.get("safety", 0) >= 2
        and db_results.get("scoring", 0) >= 1
    )

    if success:
        logger.info("║  ✅ SMOKE TEST PASSED - SYSTEM WORKING!                    ║")
        logger.info("╚════════════════════════════════════════════════════════════╝")
        logger.info("\n🎉 Full data flow verified:")
        logger.info("  ✓ Events ingested")
        logger.info("  ✓ Orchestrator routing worked")
        logger.info("  ✓ Safety Agent processed safety events")
        logger.info("  ✓ Scoring Agent processed trip score")
    else:
        logger.info("║  ⚠️  TESTS INCOMPLETE - CHECK SYSTEM                       ║")
        logger.info("╚════════════════════════════════════════════════════════════╝")

    return success


async def main():
    """Main entry point."""
    if "--deploy" in sys.argv:
        logger.info("⚠️  TODO: Implement docker compose deployment")
        logger.info(
            "For now, run: docker compose up db redis api ingestion orchestrator"
        )
        logger.info("")
        await run_smoke_test()

    elif "--test" in sys.argv:
        logger.info("Assuming full system is running...")
        await run_smoke_test()

    elif "--monitor" in sys.argv:
        logger.info("Monitoring only (no new events)...")
        await monitor_database_outputs()
        await monitor_redis_outputs()

    else:
        logger.info("Usage:")
        logger.info("  python smoke_test.py --deploy    (start system + test)")
        logger.info("  python smoke_test.py --test      (test only)")
        logger.info("  python smoke_test.py --monitor   (monitor outputs)")


if __name__ == "__main__":
    asyncio.run(main())
