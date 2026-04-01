"""
Database Repository — events table operations.

One repository per table concern. All methods are async.
DB Manager imports from here; agents never call these directly.

Location: backend/common/db/repositories/events_repo.py
"""

import json
import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


class EventsRepo:
    """
    All DB operations on the events table.
    Used by: Ingestion Tool (DB WRITE 1), DB Manager (lock lifecycle).
    """

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def event_exists(self, device_event_id: str) -> bool:
        """Idempotency check — returns True if already ingested."""
        async with self._engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT EXISTS(
                        SELECT 1 FROM pipeline_events
                        WHERE device_event_id = :device_event_id
                    )
                """),
                {"device_event_id": device_event_id},
            )
            return bool(result.scalar())

    async def acquire_lock(self, device_event_id: str) -> bool:
        """
        Phase 1 PREPARE — atomically acquire lease on an event row.

        Sets: status='processing', locked_by='orchestrator', locked_at=now()
        Only succeeds if: status='received' AND locked_by IS NULL

        Returns True if 1 row updated (lock acquired).
        Returns False if already locked or wrong status.
        """
        async with self._engine.begin() as conn:
            result = await conn.execute(
                text("""
                    UPDATE pipeline_events
                    SET    status    = 'processing',
                           locked_by = 'orchestrator',
                           locked_at = :now
                    WHERE  device_event_id = :device_event_id
                    AND    status    = 'received'
                    AND    locked_by IS NULL
                """),
                {
                    "device_event_id": device_event_id,
                    "now": datetime.now(UTC).replace(tzinfo=None),
                },
            )
            acquired = result.rowcount == 1

        if not acquired:
            logger.warning(
                {
                    "action": "lock_acquisition_failed",
                    "device_event_id": device_event_id,
                    "reason": "already_locked_or_wrong_status",
                }
            )
        else:
            logger.info(
                {
                    "action": "lock_acquired",
                    "device_event_id": device_event_id,
                }
            )

        return acquired

    async def release_lock(self, device_event_id: str) -> None:
        """
        Phase 2 COMMIT — release lease after successful agent completion.
        Sets: status='processed', locked_by=NULL, processed_at=now()
        """
        async with self._engine.begin() as conn:
            await conn.execute(
                text("""
                    UPDATE pipeline_events
                    SET    status       = 'processed',
                           locked_by    = NULL,
                           locked_at    = NULL,
                           processed_at = :now
                    WHERE  device_event_id = :device_event_id
                    AND    status = 'processing'
                """),
                {
                    "device_event_id": device_event_id,
                    "now": datetime.now(UTC).replace(tzinfo=None),
                },
            )
        logger.info(
            {
                "action": "lock_released",
                "device_event_id": device_event_id,
            }
        )

    async def get_latest_event_for_trip(self, trip_id: str) -> dict[str, Any] | None:
        """Most recent pipeline row for a trip (used after agent run to release lock)."""
        async with self._engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT device_event_id, event_id, trip_id, status
                    FROM pipeline_events
                    WHERE trip_id = :trip_id
                    ORDER BY timestamp DESC
                    LIMIT 1
                """),
                {"trip_id": trip_id},
            )
            row = result.first()
            return dict(row._mapping) if row else None

    async def fail_event(self, device_event_id: str) -> None:
        """
        Phase 2 ROLLBACK — release lease after agent failure.
        Increments retry_count. Status → 'failed'.
        """
        async with self._engine.begin() as conn:
            await conn.execute(
                text("""
                    UPDATE pipeline_events
                    SET    status      = 'failed',
                           locked_by   = NULL,
                           locked_at   = NULL,
                           retry_count = retry_count + 1
                    WHERE  device_event_id = :device_event_id
                """),
                {"device_event_id": device_event_id},
            )
        logger.warning(
            {
                "action": "event_failed",
                "device_event_id": device_event_id,
            }
        )

    async def lock_for_hitl(self, device_event_id: str) -> None:
        """
        HITL escalation — set status='locked'.
        Watchdog NEVER resets this. Only fleet manager override can exit.
        """
        async with self._engine.begin() as conn:
            await conn.execute(
                text("""
                    UPDATE pipeline_events
                    SET    status    = 'locked',
                           locked_by = NULL,
                           locked_at = NULL
                    WHERE  device_event_id = :device_event_id
                """),
                {"device_event_id": device_event_id},
            )
        logger.warning(
            {
                "action": "event_locked_hitl",
                "device_event_id": device_event_id,
            }
        )

    async def watchdog_reset_stuck(self, lock_ttl_minutes: int = 10) -> list[dict]:
        """
        Watchdog — finds events stuck in 'processing' beyond TTL.
        Resets to 'received' for reprocessing.

        CRITICAL: only touches status='processing'.
        status='locked' (HITL) is deliberately excluded.
        """
        async with self._engine.begin() as conn:
            result = await conn.execute(
                text("""
                    UPDATE pipeline_events
                    SET    status    = 'received',
                           locked_by = NULL,
                           locked_at = NULL
                    WHERE  status    = 'processing'
                    AND    locked_by = 'orchestrator'
                    AND    locked_at < now() - INTERVAL '1 minute' * :ttl
                    RETURNING device_event_id, trip_id, locked_at
                """),
                {"ttl": lock_ttl_minutes},
            )
            recovered = [dict(row) for row in result.fetchall()]

        if recovered:
            logger.warning(
                {
                    "action": "watchdog_recovered",
                    "count": len(recovered),
                    "trip_ids": [r["trip_id"] for r in recovered],
                }
            )

        return recovered

    # ===== CACHE WARMING METHODS (from improvement guide) =====

    async def get_event_by_id(self, event_id: str) -> dict[str, Any] | None:
        """
        Fetch a single event by event_id.

        Used by: Event-driven warming (Safety Agent)
        Load time: ~5-10 ms
        Data size: ~1-2 KB

        Returns:
            Dict with event data or None if not found
        """
        async with self._engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT
                        event_id,
                        trip_id,
                        event_type,
                        device_event_id,
                        timestamp,
                        data,
                        severity
                    FROM pipeline_events
                    WHERE event_id = :event_id
                """),
                {"event_id": event_id},
            )
            row = result.first()
            if not row:
                return None

            return {
                "event_id": row[0],
                "trip_id": row[1],
                "event_type": row[2],
                "device_event_id": row[3],
                "timestamp": row[4].isoformat() if row[4] else None,
                "data": json.loads(row[5]) if row[5] else {},
                "severity": row[6],
            }

    async def get_trip_metadata(self, trip_id: str) -> dict[str, Any] | None:
        """
        Fetch trip metadata (not raw telemetry).

        Used by: Event-driven warming (Safety, Support)
        Data: trip start/end, distance, duration, driver ID
        Load time: ~5 ms

        Returns:
            Dict with trip metadata or None if not found
        """
        async with self._engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT
                        trip_id,
                        driver_id,
                        truck_id,
                        started_at,
                        ended_at,
                        distance_km,
                        duration_minutes,
                        status,
                        route_name
                    FROM trips
                    WHERE trip_id = :trip_id
                """),
                {"trip_id": trip_id},
            )
            row = result.first()
            if not row:
                return None

            return {
                "trip_id": row[0],
                "driver_id": row[1],
                "truck_id": row[2],
                "started_at": row[3].isoformat() if row[3] else None,
                "ended_at": row[4].isoformat() if row[4] else None,
                "distance_km": float(row[5]) if row[5] else 0.0,
                "duration_minutes": row[6],
                "status": row[7],
                "route_name": row[8],
            }

    async def get_all_pings_for_trip(self, trip_id: str) -> list[dict[str, Any]]:
        """
        Fetch ALL pings/events for a trip.

        ⚠️  EXPENSIVE QUERY - Used only for aggregation-driven agents!

        Used by: Aggregation-driven warming (Scoring Agent at trip end)
        Load time: 1-2 seconds for 2-hour trip
        Data size: 10-50 KB for 10+ pings

        Returns:
            List of pings from trip start to end (typically 10-13 pings)
        """
        async with self._engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT
                        event_id,
                        trip_id,
                        event_type,
                        device_event_id,
                        timestamp,
                        data,
                        severity
                    FROM pipeline_events
                    WHERE trip_id = :trip_id
                    ORDER BY timestamp ASC
                """),
                {"trip_id": trip_id},
            )
            rows = result.fetchall()

            if not rows:
                return []

            pings = []
            for row in rows:
                pings.append(
                    {
                        "event_id": row[0],
                        "trip_id": row[1],
                        "event_type": row[2],
                        "device_event_id": row[3],
                        "timestamp": row[4].isoformat() if row[4] else None,
                        "data": json.loads(row[5]) if row[5] else {},
                        "severity": row[6],
                    }
                )

            return pings

    async def get_pings_count_for_trip(self, trip_id: str) -> int:
        """Get count of pings for a trip (useful for logging)."""
        async with self._engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT COUNT(*) as count FROM pipeline_events WHERE trip_id = :trip_id"
                ),
                {"trip_id": trip_id},
            )
            row = result.scalar()
            return row or 0

    async def get_rolling_average_score(
        self,
        driver_id: str,
        n: int = 3,
    ) -> float | None:
        """
        Fetch driver's rolling average score (last n trips).

        Used by: Scoring Agent (for context)
        Load time: ~10 ms

        Returns:
            Average score or None if no trips found
        """
        async with self._engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT AVG(trip_score) as avg_score
                    FROM trip_scores
                    WHERE driver_id = :driver_id
                    ORDER BY trip_id DESC
                    LIMIT :n
                """),
                {"driver_id": driver_id, "n": n},
            )
            row = result.scalar()
            return float(row) if row else None

    async def get_coaching_history(
        self,
        trip_id: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Fetch previous coaching given to this driver.

        Used by: Support Agent

        Returns:
            List of coaching records
        """
        async with self._engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT
                        coaching_id,
                        trip_id,
                        driver_id,
                        coaching_category,
                        message,
                        created_at
                    FROM coaching
                    WHERE trip_id = :trip_id
                    ORDER BY created_at DESC
                    LIMIT :limit
                """),
                {"trip_id": trip_id, "limit": limit},
            )
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows] if rows else []
