"""
DB Manager — lease-based locking and trip state transitions.

Colocated inside the Orchestrator container (not a separate service).
Owns all Postgres state transitions on behalf of the Orchestrator.

Implements optimistic locking with TTL (lease-based) — NOT strict 2PC.
  Lock acquisition:  one fast SQL UPDATE (milliseconds)
  Agent runs:        asynchronously — DB is completely free during execution
  Lock expiry:       TTL-based self-healing — watchdog resets stuck rows
  HITL protection:   status='locked' is NEVER reset by watchdog

Location: backend/agents/orchestrator/db_manager.py
"""

import logging
from datetime import datetime

from common.config.settings import get_settings
from common.db.engine import engine
from common.db.repositories import EventsRepo, TripsRepo

logger = logging.getLogger(__name__)
settings = get_settings()


class DBManager:
    """
    Owned by Orchestrator. Never called by agents directly.

    Provides:
      - acquire_lock     → Phase 1 PREPARE  (before Celery dispatch)
      - release_lock     → Phase 2 COMMIT   (after CompletionEvent)
      - fail_event       → Phase 2 ROLLBACK (after max retries)
      - lock_for_hitl    → HITL escalation  (watchdog immune)
      - update_trip      → trip status machine
      - create_trip      → on start_of_trip event
      - close_trip       → on final CompletionEvent (is_closed=True)
      - watchdog         → Celery Beat task — resets stuck 'processing' rows
    """

    def __init__(self) -> None:
        self._events = EventsRepo(engine)
        self._trips = TripsRepo(engine)

    # ── Locking ───────────────────────────────────────────────────────────────

    async def acquire_lock(self, device_event_id: str) -> bool:
        """
        MUST be called BEFORE Celery dispatch.

        Rule: lock BEFORE dispatch.
          Lock succeeds + dispatch fails  → release lock, event retried  ✅
          Dispatch succeeds + lock fails  → task runs with no DB record  ❌

        Returns True if lock acquired, False if already locked.
        """
        return await self._events.acquire_lock(device_event_id)

    async def release_lock(self, device_event_id: str) -> None:
        """Phase 2 COMMIT — called after Orchestrator receives CompletionEvent."""
        await self._events.release_lock(device_event_id)

    async def fail_event(self, device_event_id: str) -> None:
        """Phase 2 ROLLBACK — called after agent failure (max retries exceeded)."""
        await self._events.fail_event(device_event_id)

    async def lock_for_hitl(self, device_event_id: str) -> None:
        """
        HITL escalation — status → 'locked'.
        Watchdog will NEVER reset this row.
        Only fleet manager manual override can exit.
        """
        await self._events.lock_for_hitl(device_event_id)

    # ── Trip state machine ────────────────────────────────────────────────────

    async def create_trip(
        self,
        trip_id: str,
        driver_id: str,
        truck_id: str,
        started_at: datetime | None = None,
    ) -> None:
        """Called on start_of_trip event. Idempotent."""
        await self._trips.create_trip(trip_id, driver_id, truck_id, started_at)

    async def update_trip(
        self,
        trip_id: str,
        status: str,
        action_sla: str | None = None,
    ) -> None:
        """
        Update trip status. Valid transitions:
          active → scoring_pending  (on end_of_trip)
          scoring_pending → coaching_pending | complete
          coaching_pending → complete
          any → failed  (on agent error)
          any → locked  (on security violation or HITL)
        """
        await self._trips.update_status(trip_id, status, action_sla)

    async def close_trip(self, trip_id: str) -> None:
        """
        Called after final CompletionEvent (final=True).
        Sets status='complete' and capsule_closed=True.
        """
        await self._trips.close_trip(trip_id)

    async def get_rolling_avg(self, driver_id: str, n: int = 3) -> float | None:
        """
        Returns 3-trip rolling average for TripContext cache warm.
        Returns None (stub) until scoring tables are wired in Sprint 3.
        """
        return await self._trips.get_rolling_avg(driver_id, n)

    # ── Watchdog ──────────────────────────────────────────────────────────────

    async def watchdog(self) -> None:
        """
        Celery Beat task — runs every 2 minutes.

        Finds events stuck in status='processing' beyond LOCK_TTL.
        Resets to status='received' for reprocessing.

        CRITICAL RULE:
          status = 'processing' → agent crashed or timed out → reset ✅
          status = 'locked'     → HITL in progress → NEVER reset ❌

        Lock TTL must be >= 2x maximum agent runtime:
          Safety:    lock_ttl_safety   = 2 min
          Scoring:   lock_ttl_scoring  = 2 hr
          DSP:       lock_ttl_support  = 30 min
          Sentiment: lock_ttl_sentiment = 15 min
        """
        lock_ttl = settings.lock_ttl_default
        recovered = await self._events.watchdog_reset_stuck(
            lock_ttl_minutes=lock_ttl // 60
        )

        if recovered:
            logger.warning(
                {
                    "action": "watchdog_run",
                    "recovered": len(recovered),
                }
            )
        else:
            logger.debug({"action": "watchdog_run", "recovered": 0})
