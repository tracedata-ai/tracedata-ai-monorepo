"""
Integration tests for database operations during ingestion pipeline.
Tests REAL database writes and reads - not mocked.

Requires test database to be set up.
"""

from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from common.models.enums import Priority
from common.models.orm import EventORM
from core.ingestion.db import IngestionDB

# Skip all tests in this module - requires real PostgreSQL setup
pytestmark = pytest.mark.skip(reason="Requires PostgreSQL with pgvector setup")

# ── Test Database Setup ────────────────────────────────────────────────────────


@pytest.fixture
async def test_db_engine():
    """Create in-memory SQLite database for testing."""
    # Using SQLite in-memory for fast tests
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    async with engine.begin() as conn:
        # Create all tables from ORM models
        from common.models.orm import Base

        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine):
    """Create test database session."""
    async_session = sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest.fixture
async def ingestion_db(test_db_session):
    """Create IngestionDB with test session."""
    db = IngestionDB()
    db._session = test_db_session
    return db


# ── Tests ──────────────────────────────────────────────────────────────────


class TestIngestionDBInsert:
    """Tests for IngestionDB.insert_event()"""

    @pytest.mark.asyncio
    async def test_insert_event_creates_row(self, ingestion_db, test_db_session):
        """insert_event creates a row in pipeline_events table."""
        from common.models.events import TripEvent

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

        await ingestion_db.insert_event(trip_event, retry_count=0)

        # Query the database
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
        """insert_event includes all required columns including retry_count and details."""
        from common.models.events import TripEvent

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
            location={"lat": 1.30, "lon": 103.86},
            details={"collision_type": "rear_end", "speed": 45},
        )

        await ingestion_db.insert_event(trip_event, retry_count=0)

        result = await test_db_session.execute(
            select(EventORM).where(EventORM.event_id == "evt-002")
        )
        row = result.scalar_one()

        # Verify retry_count is stored
        assert row.retry_count == 0

        # Verify details JSON is stored and can be read back
        assert row.details is not None
        assert row.details["collision_type"] == "rear_end"
        assert row.details["speed"] == 45

    @pytest.mark.asyncio
    async def test_insert_event_datetime_fields_naive_utc(
        self, ingestion_db, test_db_session
    ):
        """insert_event stores datetime fields as naive UTC (no tzinfo)."""
        from common.models.events import TripEvent

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
            location={"lat": 1.31, "lon": 103.87},
            details={"reason": "driver_emergency"},
        )

        await ingestion_db.insert_event(trip_event, retry_count=0)

        result = await test_db_session.execute(
            select(EventORM).where(EventORM.event_id == "evt-003")
        )
        row = result.scalar_one()

        # Verify timestamp is stored and has NO timezone info
        assert row.timestamp is not None
        assert row.timestamp.tzinfo is None

        # Verify ingested_at also has no timezone
        assert row.ingested_at is not None
        assert row.ingested_at.tzinfo is None

    @pytest.mark.asyncio
    async def test_insert_event_priority_stored_as_string(
        self, ingestion_db, test_db_session
    ):
        """insert_event stores priority as string (PRIORITY_MAP.value), not int."""
        from common.models.events import TripEvent

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

        await ingestion_db.insert_event(trip_event, retry_count=0)

        result = await test_db_session.execute(
            select(EventORM).where(EventORM.event_id == "evt-004")
        )
        row = result.scalar_one()

        # Priority should be the string value, not an int
        assert row.priority == "high"
        assert isinstance(row.priority, str)

    @pytest.mark.asyncio
    async def test_insert_event_unique_constraints(self, ingestion_db, test_db_session):
        """insert_event respects UNIQUE constraints on event_id and device_event_id."""
        from common.models.events import TripEvent

        trip_event = TripEvent(
            event_id="evt-005",
            device_event_id="dev-005",
            trip_id="trip-005",
            truck_id="truck-005",
            driver_id="driver-005",
            event_type="acceleration",
            category="vehicle_dynamics",
            priority=Priority.LOW,
            timestamp=datetime.now(UTC),
            location={"lat": 1.33, "lon": 103.89},
            details={},
        )

        # First insert should succeed
        await ingestion_db.insert_event(trip_event, retry_count=0)

        # Duplicate insert should fail
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            await ingestion_db.insert_event(trip_event, retry_count=0)


class TestIngestionDBQuery:
    """Tests for IngestionDB.event_exists()"""

    @pytest.mark.asyncio
    async def test_event_exists_returns_true_for_existing_event(
        self, ingestion_db, test_db_session
    ):
        """event_exists returns True when event_id exists in database."""
        from common.models.events import TripEvent

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

        await ingestion_db.insert_event(trip_event, retry_count=0)

        # Query should find it
        exists = await ingestion_db.event_exists("evt-100")
        assert exists is True

    @pytest.mark.asyncio
    async def test_event_exists_returns_false_for_missing_event(self, ingestion_db):
        """event_exists returns False when event_id does not exist."""
        exists = await ingestion_db.event_exists("evt-nonexistent")
        assert exists is False
