"""
Database Repository — trips table operations.

One repository per table concern. All methods are async.
DB Manager imports from here; agents never call these directly.

Location: backend/common/db/repositories/trips_repo.py
"""

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


class TripsRepo:
    """
    All DB operations on the trips table.
    Used by: DB Manager (state transitions), Scoring Agent (rolling avg).
    """

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def create_trip(
        self,
        trip_id: str,
        driver_id: str,
        truck_id: str,
        started_at: datetime | None = None,
    ) -> None:
        """
        Called by Orchestrator on start_of_trip event.
        Inserts with status='active'. ON CONFLICT DO NOTHING — idempotent.
        """
        async with self._engine.begin() as conn:
            now = datetime.now(UTC).replace(tzinfo=None)  # naive timestamp for DB
            started_at_val = (started_at or datetime.now(UTC)).replace(tzinfo=None)
            await conn.execute(
                text("""
                    INSERT INTO pipeline_trips (trip_id, driver_id, truck_id, status, started_at, escalated, capsule_closed, created_at, updated_at)
                    VALUES (:trip_id, :driver_id, :truck_id, 'active', :started_at, false, false, :now, :now)
                    ON CONFLICT (trip_id) DO NOTHING
                """),
                {
                    "trip_id": trip_id,
                    "driver_id": driver_id,
                    "truck_id": truck_id,
                    "started_at": started_at_val,
                    "now": now,
                },
            )
        logger.info({"action": "trip_created", "trip_id": trip_id})

    async def update_status(
        self,
        trip_id: str,
        status: str,
        action_sla: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Update trips table status. Accepts optional action_sla."""
        async with self._engine.begin() as conn:
            now = datetime.now(UTC).replace(tzinfo=None)  # naive timestamp
            await conn.execute(
                text("""
                    UPDATE pipeline_trips
                    SET    status     = :status,
                           action_sla = COALESCE(:action_sla, action_sla),
                           updated_at = :now
                    WHERE  trip_id = :trip_id
                """),
                {
                    "trip_id": trip_id,
                    "status": status,
                    "action_sla": action_sla,
                    "now": now,
                },
            )
        logger.info(
            {"action": "trip_status_updated", "trip_id": trip_id, "status": status}
        )

    async def get_truck_and_driver(self, trip_id: str) -> tuple[str, str] | None:
        """Return (truck_id, driver_id) for a trip if the row exists."""
        async with self._engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT truck_id, driver_id
                    FROM   pipeline_trips
                    WHERE  trip_id = :trip_id
                """),
                {"trip_id": trip_id},
            )
            row = result.first()
            if not row:
                return None
            m = row._mapping
            return (str(m["truck_id"]), str(m["driver_id"]))

    async def close_trip(self, trip_id: str) -> None:
        """Mark trip as complete and capsule as closed after final CompletionEvent."""
        async with self._engine.begin() as conn:
            now = datetime.now(UTC).replace(tzinfo=None)  # naive timestamp
            await conn.execute(
                text("""
                    UPDATE pipeline_trips
                    SET    status         = 'complete',
                           capsule_closed = true,
                           closed_at      = :now,
                           updated_at     = :now
                    WHERE  trip_id = :trip_id
                """),
                {"trip_id": trip_id, "now": now},
            )
        logger.info({"action": "trip_closed", "trip_id": trip_id})

    async def get_rolling_avg(self, driver_id: str, n: int = 3) -> float | None:
        """
        Returns the average behaviour_score for the last n completed trips.
        Returns None if fewer than n completed trips exist.
        Used by Orchestrator to warm TripContext cache.

        NOTE: Sprint 3 — requires trip_scores table. Returns None (stub) until then.
        """
        # TODO Sprint 3 — wire to scoring.trip_scores table
        # async with self._engine.connect() as conn:
        #     result = await conn.execute(
        #         text("""
        #             SELECT AVG(behaviour_score)
        #             FROM   (
        #                 SELECT ts.behaviour_score
        #                 FROM   scoring.trip_scores ts
        #                 JOIN   trips t ON ts.trip_id = t.trip_id
        #                 WHERE  t.driver_id = :driver_id
        #                 AND    t.status    = 'complete'
        #                 ORDER  BY t.ended_at DESC
        #                 LIMIT  :n
        #             ) sub
        #         """),
        #         {"driver_id": driver_id, "n": n},
        #     )
        #     return result.scalar()
        return None
