"""
Integration tests for database repositories - event lock lifecycle.
Tests REAL database operations for acquire_lock, release_lock, fail_event.

Requires test database to be set up.
"""

from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from common.db.repositories.events_repo import EventsRepo
from common.models.enums import Priority
from common.models.events import TripEvent
from common.models.orm import EventORM

# Skip all tests in this module - requires real PostgreSQL setup
pytestmark = pytest.mark.skip(reason="Requires PostgreSQL with pgvector setup")


@pytest.fixture
async def test_db_engine():
    """Create in-memory SQLite database for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    async with engine.begin() as conn:
        from common.models.sa_base import Base

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
async def events_repo(test_db_session):
    """Create EventsRepo with test session."""
    repo = EventsRepo(test_db_session)
    return repo


@pytest.fixture
async def sample_event(test_db_session):
    """Create a sample event in the database."""

    trip_event = TripEvent(
        event_id="evt-lock-001",
        device_event_id="dev-lock-001",
        trip_id="trip-lock-001",
        truck_id="truck-lock-001",
        driver_id="driver-lock-001",
        event_type="harsh_brake",
        category="harsh_events",
        priority=Priority.HIGH,
        timestamp=datetime.now(UTC),
        offset_seconds=10,
        location={"lat": 1.29, "lon": 103.85},
        details={"g_force": -0.85},
    )

    from core.ingestion.db import IngestionDB

    db = IngestionDB()
    db._session = test_db_session
    await db.insert_event(trip_event, retry_count=0)

    return trip_event


class TestEventRepositoryLocks:
    """Tests for EventsRepo lock lifecycle (acquire, release, fail)"""

    @pytest.mark.asyncio
    async def test_acquire_lock_sets_locked_fields(
        self, events_repo, test_db_session, sample_event
    ):
        """acquire_lock sets locked_by and locked_at fields."""
        orchestrator_id = "orchestrator-1"

        result = await events_repo.acquire_lock(
            sample_event.device_event_id, orchestrator_id
        )

        # Should return the orchestrator_id on success
        assert result == orchestrator_id

        # Verify fields in database
        db_event = await test_db_session.execute(
            select(EventORM).where(
                EventORM.device_event_id == sample_event.device_event_id
            )
        )
        event = db_event.scalar_one()

        assert event.locked_by == orchestrator_id
        assert event.locked_at is not None
        assert event.locked_at.tzinfo is None  # Should be naive UTC

    @pytest.mark.asyncio
    async def test_acquire_lock_fails_if_already_locked(
        self, events_repo, test_db_session, sample_event
    ):
        """acquire_lock returns None if event is already locked by another."""
        orchestrator_1 = "orchestrator-1"
        orchestrator_2 = "orchestrator-2"

        # First lock succeeds
        result1 = await events_repo.acquire_lock(
            sample_event.device_event_id, orchestrator_1
        )
        assert result1 == orchestrator_1

        # Second lock fails
        result2 = await events_repo.acquire_lock(
            sample_event.device_event_id, orchestrator_2
        )
        assert result2 is None

    @pytest.mark.asyncio
    async def test_release_lock_clears_locked_fields(
        self, events_repo, test_db_session, sample_event
    ):
        """release_lock clears locked_by and locked_at fields."""
        orchestrator_id = "orchestrator-1"

        # Acquire lock
        await events_repo.acquire_lock(sample_event.device_event_id, orchestrator_id)

        # Release lock
        await events_repo.release_lock(sample_event.device_event_id)

        # Verify fields are cleared
        db_event = await test_db_session.execute(
            select(EventORM).where(
                EventORM.device_event_id == sample_event.device_event_id
            )
        )
        event = db_event.scalar_one()

        assert event.locked_by is None
        assert event.locked_at is None

    @pytest.mark.asyncio
    async def test_fail_event_sets_failed_status_and_increments_retry(
        self, events_repo, test_db_session, sample_event
    ):
        """fail_event sets status to 'failed' and increments retry_count."""
        orchestrator_id = "orchestrator-1"

        # Acquire and then fail
        await events_repo.acquire_lock(sample_event.device_event_id, orchestrator_id)

        await events_repo.fail_event(sample_event.device_event_id)

        # Verify status and retry count
        db_event = await test_db_session.execute(
            select(EventORM).where(
                EventORM.device_event_id == sample_event.device_event_id
            )
        )
        event = db_event.scalar_one()

        assert event.status == "failed"
        assert event.retry_count > 0
        assert event.locked_by is None  # Should be cleared

    @pytest.mark.asyncio
    async def test_fail_event_successive_retries(
        self, events_repo, test_db_session, sample_event
    ):
        """fail_event can be called multiple times to track retry attempts."""
        orchestrator_id = "orchestrator-1"

        # Fail event 3 times
        for _attempt in range(3):
            await events_repo.acquire_lock(
                sample_event.device_event_id, orchestrator_id
            )
            await events_repo.fail_event(sample_event.device_event_id)

        # Verify retry_count is 3
        db_event = await test_db_session.execute(
            select(EventORM).where(
                EventORM.device_event_id == sample_event.device_event_id
            )
        )
        event = db_event.scalar_one()

        assert event.retry_count == 3

    @pytest.mark.asyncio
    async def test_lock_datetime_is_naive_utc(
        self, events_repo, test_db_session, sample_event
    ):
        """Lock datetime should be naive UTC (no timezone info)."""
        orchestrator_id = "orchestrator-1"

        await events_repo.acquire_lock(sample_event.device_event_id, orchestrator_id)

        db_event = await test_db_session.execute(
            select(EventORM).where(
                EventORM.device_event_id == sample_event.device_event_id
            )
        )
        event = db_event.scalar_one()

        # locked_at should have no timezone
        assert event.locked_at.tzinfo is None
