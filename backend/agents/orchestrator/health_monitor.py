"""
Redis Health Monitor — background coroutine inside Orchestrator container.

Watches active trip keys in Redis for anomalies:
  - TripContext TTL miss mid-trip (triggers cache rebuild)
  - Agent output missing after SLA window (triggers alert)

Runs as a daemon thread inside the Orchestrator process.
Not a separate container — colocated with Orchestrator.

Sprint 2: stub — starts thread but does nothing (logs heartbeat only).
Phase 5:  full implementation — TTL miss detection and cache rebuild.

Location: backend/agents/orchestrator/health_monitor.py
"""

import logging
import threading
import time

logger = logging.getLogger(__name__)

# How often the monitor checks active trip keys (seconds)
CHECK_INTERVAL_SECONDS = 30


class RedisHealthMonitor:
    """
    Background thread that monitors Redis state for active trips.

    Responsibilities (Phase 5):
      1. Detect TripContext TTL misses mid-trip
         → acquire SETNX rebuild lock
         → reload from Postgres via DB Manager
         → re-warm Redis cache
         → publish context_ready to cache-anomalies channel

      2. Detect agent output missing after SLA window
         → publish SLA breach to monitor:cache-anomalies channel
         → Orchestrator reacts (retry or HITL)

    Sprint 2 stub:
      Thread starts and logs a heartbeat every 30 seconds.
      No actual monitoring — safe to run without any side effects.
    """

    def __init__(self, redis=None, db_manager=None) -> None:
        self._redis = redis
        self._db_manager = db_manager
        self._running = False
        self._thread: threading.Thread | None = None
        self.active_trips: set[str] = set()

    def start(self) -> None:
        """Start the background monitoring thread."""
        self._running = True
        self._thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="redis-health-monitor",
        )
        self._thread.start()
        logger.info({"action": "health_monitor_started"})

    def stop(self) -> None:
        """Signal the monitoring thread to stop."""
        self._running = False
        logger.info({"action": "health_monitor_stopped"})

    def register_trip(self, trip_id: str) -> None:
        """Called by Orchestrator when a new trip is dispatched."""
        self.active_trips.add(trip_id)

    def deregister_trip(self, trip_id: str) -> None:
        """Called by Orchestrator when a trip is closed."""
        self.active_trips.discard(trip_id)

    # ── Monitor loop ──────────────────────────────────────────────────────────

    def _monitor_loop(self) -> None:
        while self._running:
            try:
                self._check_active_trips()
            except Exception as e:
                logger.error({"action": "health_monitor_error", "error": str(e)})
            time.sleep(CHECK_INTERVAL_SECONDS)

    def _check_active_trips(self) -> None:
        """
        Sprint 2 stub — logs heartbeat only.

        Phase 5 implementation:
          for trip_id in self.active_trips:
              context_key = RedisSchema.Trip.context(trip_id)
              exists = asyncio.run(self._redis.get_trip_context(context_key))
              if not exists:
                  self._handle_context_miss(trip_id)
        """
        if self.active_trips:
            logger.debug(
                {
                    "action": "health_monitor_check",
                    "active_trips": len(self.active_trips),
                    "status": "stub_no_op",
                }
            )

    def _handle_context_miss(self, trip_id: str) -> None:
        """
        Phase 5 — cache rebuild on TTL miss.

        1. Acquire SETNX rebuild lock (prevent thundering herd)
        2. Reload TripContext from Postgres via DB Manager
        3. Re-warm Redis cache
        4. Publish context_ready to cache-anomalies channel
        5. Release SETNX lock
        """
        # TODO Phase 5
        pass
