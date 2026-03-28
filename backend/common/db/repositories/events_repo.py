"""
Database Repository — events table operations.

One repository per table concern. All methods are async.
DB Manager imports from here; agents never call these directly.

Location: backend/common/db/repositories/events_repo.py
"""

import logging
from datetime import UTC, datetime

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
                        SELECT 1 FROM events
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
                    UPDATE events
                    SET    status    = 'processing',
                           locked_by = 'orchestrator',
                           locked_at = :now
                    WHERE  device_event_id = :device_event_id
                    AND    status    = 'received'
                    AND    locked_by IS NULL
                """),
                {
                    "device_event_id": device_event_id,
                    "now": datetime.now(UTC),
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
                    UPDATE events
                    SET    status       = 'processed',
                           locked_by    = NULL,
                           locked_at    = NULL,
                           processed_at = :now
                    WHERE  device_event_id = :device_event_id
                    AND    status = 'processing'
                """),
                {
                    "device_event_id": device_event_id,
                    "now": datetime.now(UTC),
                },
            )
        logger.info(
            {
                "action": "lock_released",
                "device_event_id": device_event_id,
            }
        )

    async def fail_event(self, device_event_id: str) -> None:
        """
        Phase 2 ROLLBACK — release lease after agent failure.
        Increments retry_count. Status → 'failed'.
        """
        async with self._engine.begin() as conn:
            await conn.execute(
                text("""
                    UPDATE events
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
                    UPDATE events
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
                    UPDATE events
                    SET    status    = 'received',
                           locked_by = NULL,
                           locked_at = NULL
                    WHERE  status    = 'processing'
                    AND    locked_by = 'orchestrator'
                    AND    locked_at < now() - INTERVAL ':ttl minutes'
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
