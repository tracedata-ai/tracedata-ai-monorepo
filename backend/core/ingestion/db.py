"""
Ingestion Database Layer — async SQLAlchemy with asyncpg driver.

Handles:
  - Idempotency checks  (device_event_id lookup before insert)
  - DB WRITE 1          (INSERT into events table, status=received)
  - Connection pool management

All queries are async-safe. Uses SQLAlchemy Core (not ORM)
for explicit SQL control over the events table.

Location: backend/core/ingestion/db.py
"""

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from common.config.events import EVENT_MATRIX, PRIORITY_MAP
from common.config.settings import get_settings
from common.models.events import TelemetryPacket

settings = get_settings()

logger = logging.getLogger(__name__)


class IngestionDB:
    """
    Async database client for the Ingestion Tool.
    One instance shared across the worker lifecycle.

    Use as an async context manager:
        async with IngestionDB() as db:
            await db.insert_event(packet)
    """

    def __init__(self, dsn: str | None = None) -> None:
        self._dsn: str = dsn or settings.database_url
        self._engine: AsyncEngine | None = None

    # ── LIFECYCLE ─────────────────────────────────────────────────────────────

    async def connect(self) -> None:
        """Creates the async connection pool. Call once at startup."""
        self._engine = create_async_engine(
            self._dsn,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # validates connections before use
            echo=False,
        )
        # Log DSN without password
        safe_dsn = self._dsn.split("@")[-1]
        logger.info({"action": "db_connected", "dsn": safe_dsn})

    async def disconnect(self) -> None:
        """Disposes connection pool. Call on shutdown."""
        if self._engine:
            await self._engine.dispose()
            logger.info({"action": "db_disconnected"})

    # ── IDEMPOTENCY ───────────────────────────────────────────────────────────

    async def event_exists(self, device_event_id: str) -> bool:
        """
        Returns True if device_event_id already exists in events table.
        Uses the partial index on (device_event_id) — sub-millisecond lookup.
        """
        async with self._engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT EXISTS(
                        SELECT 1 FROM events
                        WHERE device_event_id = :device_event_id
                    )
                """),
                {"device_event_id": device_event_id},
            )
            return result.scalar()

    # ── WRITE ─────────────────────────────────────────────────────────────────

    async def insert_event(self, packet: TelemetryPacket) -> None:
        """
        DB WRITE 1 — inserts raw event into events table.
        Sets status = 'received' on insert.
        ON CONFLICT DO NOTHING — belt-and-suspenders deduplication
        (idempotency check in step 5 is the primary guard).

        IMPORTANT: driver_id written here is the REAL driver ID.
        This is the only table that stores the real identity.
        All other tables use the anonymised DRV-ANON-XXXX token.
        """
        event = packet.event
        config = EVENT_MATRIX[event.event_type]
        lat = event.location.lat if event.location else None
        lon = event.location.lon if event.location else None

        async with self._engine.begin() as conn:
            await conn.execute(
                text("""
                    INSERT INTO events (
                        device_event_id,
                        event_id,
                        trip_id,
                        driver_id,
                        truck_id,
                        event_type,
                        category,
                        priority,
                        ping_type,
                        source,
                        is_emergency,
                        timestamp,
                        offset_seconds,
                        trip_meter_km,
                        odometer_km,
                        lat,
                        lon,
                        raw_payload,
                        status,
                        ingested_at
                    ) VALUES (
                        :device_event_id,
                        :event_id,
                        :trip_id,
                        :driver_id,
                        :truck_id,
                        :event_type,
                        :category,
                        :priority,
                        :ping_type,
                        :source,
                        :is_emergency,
                        :timestamp,
                        :offset_seconds,
                        :trip_meter_km,
                        :odometer_km,
                        :lat,
                        :lon,
                        :raw_payload,
                        'received',
                        :ingested_at
                    )
                    ON CONFLICT (device_event_id) DO NOTHING
                """),
                {
                    "device_event_id": event.device_event_id,
                    "event_id": event.event_id,
                    "trip_id": event.trip_id,
                    "driver_id": event.driver_id,  # real ID — audit only
                    "truck_id": event.truck_id,
                    "event_type": event.event_type,
                    "category": config.category,
                    "priority": PRIORITY_MAP[event.priority],
                    "ping_type": packet.ping_type.value,
                    "source": packet.source.value,
                    "is_emergency": packet.is_emergency,
                    "timestamp": event.timestamp,
                    "offset_seconds": event.offset_seconds,
                    "trip_meter_km": event.trip_meter_km,
                    "odometer_km": event.odometer_km,
                    "lat": lat,
                    "lon": lon,
                    "raw_payload": packet.model_dump_json(),
                    "ingested_at": datetime.now(UTC),
                },
            )

        logger.info(
            {
                "action": "event_written",
                "trip_id": event.trip_id,
                "event_id": event.event_id,
                "device_event_id": event.device_event_id,
                "event_type": event.event_type,
            }
        )

    # ── CONTEXT MANAGER ───────────────────────────────────────────────────────

    async def __aenter__(self) -> "IngestionDB":
        await self.connect()
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.disconnect()
