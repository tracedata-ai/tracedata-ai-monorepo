"""
Integration tests for EventsRepo lock lifecycle (SQLite in-memory).

Uses async SQLAlchemy + aiosqlite — no Docker Postgres required.
"""

from datetime import UTC, datetime

import pytest
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from common.db.repositories.events_repo import EventsRepo
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
def events_repo(test_db_engine):
    return EventsRepo(test_db_engine)


def _packet(event: TripEvent) -> TelemetryPacket:
    return TelemetryPacket(
        ping_type=PingType.BATCH,
        source=Source.TELEMATICS_DEVICE,
        is_emergency=False,
        event=event,
    )


@pytest.fixture
async def sample_event(test_db_engine):
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
    db = IngestionDB()
    db._engine = test_db_engine
    await db.insert_event(_packet(trip_event))
    return trip_event


class TestEventRepositoryLocks:
    @pytest.mark.asyncio
    async def test_acquire_lock_sets_locked_fields(
        self, events_repo, test_db_session, sample_event
    ):
        assert await events_repo.acquire_lock(sample_event.device_event_id) is True

        db_event = await test_db_session.execute(
            select(EventORM).where(
                EventORM.device_event_id == sample_event.device_event_id
            )
        )
        event = db_event.scalar_one()
        assert event.locked_by == "orchestrator"
        assert event.status == "processing"
        assert event.locked_at is not None
        assert event.locked_at.tzinfo is None

    @pytest.mark.asyncio
    async def test_acquire_lock_fails_if_already_locked(
        self, events_repo, sample_event
    ):
        assert await events_repo.acquire_lock(sample_event.device_event_id) is True
        assert await events_repo.acquire_lock(sample_event.device_event_id) is False

    @pytest.mark.asyncio
    async def test_release_lock_clears_locked_fields(
        self, events_repo, test_db_session, sample_event
    ):
        await events_repo.acquire_lock(sample_event.device_event_id)
        await events_repo.release_lock(sample_event.device_event_id)

        db_event = await test_db_session.execute(
            select(EventORM).where(
                EventORM.device_event_id == sample_event.device_event_id
            )
        )
        event = db_event.scalar_one()
        assert event.locked_by is None
        assert event.locked_at is None
        assert event.status == "processed"
        assert event.processed_at is not None

    @pytest.mark.asyncio
    async def test_fail_event_sets_failed_status_and_increments_retry(
        self, events_repo, test_db_session, sample_event
    ):
        await events_repo.acquire_lock(sample_event.device_event_id)
        await events_repo.fail_event(sample_event.device_event_id)

        db_event = await test_db_session.execute(
            select(EventORM).where(
                EventORM.device_event_id == sample_event.device_event_id
            )
        )
        event = db_event.scalar_one()
        assert event.status == "failed"
        assert event.retry_count == 1
        assert event.locked_by is None

    @pytest.mark.asyncio
    async def test_fail_event_successive_retries(
        self, events_repo, test_db_session, sample_event
    ):
        dev_id = sample_event.device_event_id
        for _ in range(3):
            await test_db_session.execute(
                update(EventORM)
                .where(EventORM.device_event_id == dev_id)
                .values(status="received", locked_by=None, locked_at=None)
            )
            await test_db_session.commit()
            assert await events_repo.acquire_lock(dev_id) is True
            await events_repo.fail_event(dev_id)

        db_event = await test_db_session.execute(
            select(EventORM).where(EventORM.device_event_id == dev_id)
        )
        assert db_event.scalar_one().retry_count == 3

    @pytest.mark.asyncio
    async def test_lock_datetime_is_naive_utc(
        self, events_repo, test_db_session, sample_event
    ):
        await events_repo.acquire_lock(sample_event.device_event_id)
        db_event = await test_db_session.execute(
            select(EventORM).where(
                EventORM.device_event_id == sample_event.device_event_id
            )
        )
        event = db_event.scalar_one()
        assert event.locked_at is not None
        assert event.locked_at.tzinfo is None
