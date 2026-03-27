from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.models.events import TripEvent
from common.models.orm import EventORM


class IngestionDB:
    """
    DB Helper for the Ingestion Tool.
    Handles Idempotency check and first DB Write.
    """

    @staticmethod
    async def event_exists(session: AsyncSession, device_event_id: str) -> bool:
        """
        Step 5: Idempotency check.
        Checks if this device_event_id has already been ingested.
        """
        query = select(EventORM).where(EventORM.device_event_id == device_event_id)
        result = await session.execute(query)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def save_event(session: AsyncSession, event: TripEvent) -> EventORM:
        """
        Step 6: DB Write 1.
        Saves the clean TripEvent to Postgres with status 'received'.
        """
        orm_event = EventORM(
            event_id=event.event_id,
            device_event_id=event.device_event_id,
            trip_id=event.trip_id,
            truck_id=event.truck_id,
            driver_id=event.driver_id,
            event_type=event.event_type,
            category=event.category,
            priority=event.priority.value,
            timestamp=event.timestamp.replace(tzinfo=None),
            offset_seconds=event.offset_seconds,
            trip_meter_km=event.trip_meter_km,
            odometer_km=event.odometer_km,
            lat=event.location.lat if event.location else None,
            lon=event.location.lon if event.location else None,
            details=event.details,
            status="received",
        )

        session.add(orm_event)
        await session.commit()
        await session.refresh(orm_event)
        return orm_event
