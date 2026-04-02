"""
Integration tests for IngestionDB against SQLite in-memory.

Uses the same insert_event / event_exists code paths as production.
"""

from datetime import UTC, datetime

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from common.models.enums import PingType, Priority, Source
from common.models.events import TelemetryPacket, TripEvent
from common.models.orm import EventORM
from core.ingestion.db import IngestionDB

pytestmark = pytest.mark.integration


@pytest.fixture
async def test_db_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(EventORM.__table__.create)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine):
    async_session = sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture
def ingestion_db(test_db_engine):
    db = IngestionDB()
    db._engine = test_db_engine
    return db


def _packet(event: TripEvent) -> TelemetryPacket:
    return TelemetryPacket(
        ping_type=PingType.BATCH,
        source=Source.TELEMATICS_DEVICE,
        is_emergency=False,
        event=event,
    )


class TestIngestionDBInsert:
    @pytest.mark.asyncio
    async def test_insert_event_creates_row(self, ingestion_db, test_db_session):
        trip_event = TripEvent(
            event_id="evt-001",
            device_event_id="dev-001",
            trip_id="trip-001",
            truck_id="truck-001",
            driver_id="driver-001",
            event_type="harsh_brake",
            category="harsh_events",
            priority=Priority.HIGH,
            timestamp=datetime.now(UTC),
            offset_seconds=20,
            location={"lat": 1.29, "lon": 103.85},
            details={"g_force": -0.85},
        )
        await ingestion_db.insert_event(_packet(trip_event))

        result = await test_db_session.execute(
            select(EventORM).where(EventORM.event_id == "evt-001")
        )
        row = result.scalar_one_or_none()
        assert row is not None
        assert row.event_id == "evt-001"
        assert row.device_event_id == "dev-001"
        assert row.truck_id == "truck-001"

    @pytest.mark.asyncio
    async def test_insert_event_stores_all_required_columns(
        self, ingestion_db, test_db_session
    ):
        trip_event = TripEvent(
            event_id="evt-002",
            device_event_id="dev-002",
            trip_id="trip-002",
            truck_id="truck-002",
            driver_id="driver-002",
            event_type="collision",
            category="safety",
            priority=Priority.CRITICAL,
            timestamp=datetime.now(UTC),
            offset_seconds=0,
            location={"lat": 1.30, "lon": 103.86},
            details={"collision_type": "rear_end", "speed": 45},
        )
        await ingestion_db.insert_event(_packet(trip_event))

        result = await test_db_session.execute(
            select(EventORM).where(EventORM.event_id == "evt-002")
        )
        row = result.scalar_one()
        assert row.retry_count == 0
        assert row.details is not None
        assert row.details["collision_type"] == "rear_end"
        assert row.details["speed"] == 45

    @pytest.mark.asyncio
    async def test_insert_event_datetime_fields_naive_utc(
        self, ingestion_db, test_db_session
    ):
        now_utc = datetime.now(UTC)
        trip_event = TripEvent(
            event_id="evt-003",
            device_event_id="dev-003",
            trip_id="trip-003",
            truck_id="truck-003",
            driver_id="driver-003",
            event_type="driver_sos",
            category="emergency",
            priority=Priority.CRITICAL,
            timestamp=now_utc,
            offset_seconds=0,
            location={"lat": 1.31, "lon": 103.87},
            details={"reason": "driver_emergency"},
        )
        await ingestion_db.insert_event(_packet(trip_event))

        result = await test_db_session.execute(
            select(EventORM).where(EventORM.event_id == "evt-003")
        )
        row = result.scalar_one()
        assert row.timestamp is not None
        assert row.timestamp.tzinfo is None
        assert row.ingested_at is not None
        assert row.ingested_at.tzinfo is None

    @pytest.mark.asyncio
    async def test_insert_event_priority_stored_as_string(
        self, ingestion_db, test_db_session
    ):
        trip_event = TripEvent(
            event_id="evt-004",
            device_event_id="dev-004",
            trip_id="trip-004",
            truck_id="truck-004",
            driver_id="driver-004",
            event_type="harsh_brake",
            category="harsh_events",
            priority=Priority.HIGH,
            timestamp=datetime.now(UTC),
            offset_seconds=40,
            location={"lat": 1.32, "lon": 103.88},
            details={},
        )
        await ingestion_db.insert_event(_packet(trip_event))

        result = await test_db_session.execute(
            select(EventORM).where(EventORM.event_id == "evt-004")
        )
        row = result.scalar_one()
        assert row.priority == "high"
        assert isinstance(row.priority, str)

    @pytest.mark.asyncio
    async def test_insert_event_duplicate_device_id_is_noop(
        self, ingestion_db, test_db_session
    ):
        """ON CONFLICT (device_event_id) DO NOTHING — no IntegrityError."""
        trip_event = TripEvent(
            event_id="evt-005",
            device_event_id="dev-005",
            trip_id="trip-005",
            truck_id="truck-005",
            driver_id="driver-005",
            event_type="hard_accel",
            category="harsh_events",
            priority=Priority.LOW,
            timestamp=datetime.now(UTC),
            offset_seconds=0,
            location={"lat": 1.33, "lon": 103.89},
            details={},
        )
        await ingestion_db.insert_event(_packet(trip_event))
        await ingestion_db.insert_event(_packet(trip_event))

        cnt = await test_db_session.execute(
            select(func.count())
            .select_from(EventORM)
            .where(EventORM.device_event_id == "dev-005")
        )
        assert cnt.scalar_one() == 1


class TestIngestionDBQuery:
    @pytest.mark.asyncio
    async def test_event_exists_returns_true_for_existing_device_event(
        self, ingestion_db
    ):
        trip_event = TripEvent(
            event_id="evt-100",
            device_event_id="dev-100",
            trip_id="trip-100",
            truck_id="truck-100",
            driver_id="driver-100",
            event_type="rollover",
            category="safety",
            priority=Priority.CRITICAL,
            timestamp=datetime.now(UTC),
            offset_seconds=100,
            location={"lat": 1.34, "lon": 103.90},
            details={},
        )
        await ingestion_db.insert_event(_packet(trip_event))
        assert await ingestion_db.event_exists("dev-100") is True

    @pytest.mark.asyncio
    async def test_event_exists_returns_false_for_missing_device_event(
        self, ingestion_db
    ):
        assert await ingestion_db.event_exists("dev-nonexistent") is False
