"""
Smoke verification inside Docker network: buffer → ingestion → pipeline_events.

Usage (from repo root):
  docker compose exec -T api python scripts/docker_verify_flow.py

Requires: db + redis + schema applied (bootstrap_e2e.sql + agent_schemas.sql).
"""

from __future__ import annotations

import asyncio
import json
import uuid
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from common.config.settings import get_settings
from common.models.enums import PingType, Priority, Source
from common.models.events import Location, TripEvent
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

settings = get_settings()
TRUCK_ID = "VERIFY-TRUCK-001"


def _packet() -> dict:
    now = datetime.now(UTC)
    trip_id = f"TRIP-VERIFY-{uuid.uuid4().hex[:8]}"
    ev_id = str(uuid.uuid4())
    te = TripEvent(
        event_id=ev_id,
        device_event_id=f"DEV-{uuid.uuid4().hex[:12]}",
        trip_id=trip_id,
        truck_id=TRUCK_ID,
        driver_id="DRV-VERIFY-1",
        event_type="normal_operation",
        category="telemetry",
        priority=Priority.LOW,
        timestamp=now,
        offset_seconds=0,
        location=Location(lat=40.71, lon=-74.0),
    )
    return {
        "ping_type": PingType.MEDIUM_SPEED.value,
        "source": Source.TELEMATICS_DEVICE.value,
        "is_emergency": False,
        "event": json.loads(te.model_dump_json()),
    }


async def main() -> None:
    print("settings.database_url host:", settings.database_url.split("@")[-1])
    raw = _packet()
    trip_id = raw["event"]["trip_id"]
    key = RedisSchema.Telemetry.buffer(TRUCK_ID)

    redis = RedisClient()
    try:
        await redis._client.delete(key)
        payload = json.dumps(raw)
        await redis._client.zadd(key, mapping={payload: 9})
        print(f"pushed 1 packet to {key} trip_id={trip_id}")
    finally:
        await redis.close()

    await asyncio.sleep(5)

    engine = create_async_engine(settings.database_url, echo=False)
    try:
        async with engine.connect() as conn:
            n = (
                await conn.execute(
                    text("SELECT COUNT(*) FROM pipeline_events WHERE trip_id = :t"),
                    {"t": trip_id},
                )
            ).scalar()
            print("pipeline_events rows for this trip:", int(n or 0))
            if int(n or 0) >= 1:
                print("OK: ingestion wrote to Postgres")
            else:
                print("FAIL: no pipeline_events row (check ingestion logs, schema)")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
