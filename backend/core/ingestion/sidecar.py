"""
Ingestion Sidecar — main pipeline entry point.

Runs as an independent async worker. Watches the raw buffer,
processes each event through the 7-step pipeline, then routes to:
  - processed queue   → on success (clean TripEvent)
  - dead letter queue → on any rejection (raw packet + reason)

Orchestrator reads ONLY from the processed queue.
It never sees raw TelemetryPackets.

Pipeline steps:
  1. Schema validation    (Pydantic)
  2. EVENT_MATRIX check   (governance — unknown types rejected)
  3. Injection scan       (OWASP LLM01 — prompt, SQL, HTML, control chars)
  4. PII scrub            (OWASP LLM02 — driver_id, GPS, injury)
  5. Idempotency check    (device_event_id dedup against Postgres)
  6. Postgres write       (DB WRITE 1, status=received)
  7a. Push to processed   → clean TripEvent JSON → Orchestrator
  7b. Push to DLQ         → raw packet + reason → fleet admin (TTL 48h)

Location: backend/core/ingestion/sidecar.py
"""

import asyncio
import json
import logging
from typing import Any

from pydantic import ValidationError

from common.models.events        import TelemetryPacket, TripEvent
from common.config.events        import EVENT_MATRIX, PRIORITY_MAP
from common.redis.keys           import RedisSchema
from core.ingestion.db           import IngestionDB
from core.ingestion.injection    import InjectionScanner
from core.ingestion.transformer  import PacketTransformer
from security.pii                import PIIScrubber

logger = logging.getLogger(__name__)


class IngestionResult:
    """Carries the outcome of one ingestion attempt."""

    __slots__ = ("trip_event", "rejected", "reason")

    def __init__(
        self,
        trip_event: TripEvent | None = None,
        rejected:   bool             = False,
        reason:     str | None       = None,
    ) -> None:
        self.trip_event = trip_event
        self.rejected   = rejected
        self.reason     = reason

    @property
    def ok(self) -> bool:
        return self.trip_event is not None

    def __repr__(self) -> str:
        if self.ok:
            return f"<IngestionResult ok trip_id={self.trip_event.trip_id}>"
        return f"<IngestionResult rejected reason={self.reason}>"


class IngestionSidecar:
    """
    Deterministic security boundary between Redis raw buffer and Orchestrator.

    - No LLM
    - No decisions — pure validation + transformation
    - Fully async — safe for use in async worker loop
    - Pushes to processed queue on success
    - Pushes to DLQ on any rejection (with structured reason code)

    Usage (worker loop):
        async with IngestionDB() as db:
            redis   = RedisClient()
            sidecar = IngestionSidecar(db=db, redis=redis)
            await sidecar.run_worker(truck_id="T12345")
    """

    def __init__(self, db: IngestionDB, redis: Any) -> None:
        self._db          = db
        self._redis       = redis
        self._scanner     = InjectionScanner()
        self._scrubber    = PIIScrubber()
        self._transformer = PacketTransformer()

    # ── PUBLIC ────────────────────────────────────────────────────────────────

    async def process(
        self,
        raw:      dict[str, Any],
        truck_id: str,
        raw_json: str | None = None,
    ) -> IngestionResult:
        """
        Main pipeline entry point.
        Routes to processed queue or DLQ based on outcome.
        Returns IngestionResult — never raises.

        Args:
            raw:      parsed dict from Redis buffer
            truck_id: truck identifier for queue routing
            raw_json: original JSON string (for DLQ — preserves exact payload)
        """
        if raw_json is None:
            raw_json = json.dumps(raw)

        # Determine priority for queue routing before any validation
        priority_str   = raw.get("event", {}).get("priority", "low")
        priority_score = PRIORITY_MAP.get(priority_str, 9)

        # ── Step 1: Schema validation ─────────────────────────────────────────
        packet = self._validate_schema(raw)
        if packet is None:
            return await self._reject(truck_id, raw_json, priority_score, "schema_invalid")

        ctx = {
            "trip_id":         packet.event.trip_id,
            "event_id":        packet.event.event_id,
            "device_event_id": packet.event.device_event_id,
            "event_type":      packet.event.event_type,
        }

        # ── Step 2: EVENT_MATRIX governance check ─────────────────────────────
        if not self._check_event_matrix(packet, ctx):
            return await self._reject(truck_id, raw_json, priority_score, "unknown_event_type")

        # Update priority from governed value (EVENT_MATRIX overrides device)
        priority_score = PRIORITY_MAP.get(packet.event.priority, 9)

        # ── Step 3: Injection scan ────────────────────────────────────────────
        clean, reason = self._scanner.scan(raw)
        if not clean:
            logger.warning({**ctx, "action": "injection_blocked", "reason": reason})
            return await self._reject(truck_id, raw_json, priority_score, f"injection:{reason}")

        # ── Step 4: PII scrub ─────────────────────────────────────────────────
        packet = self._scrub_pii(packet)

        # ── Step 5: Idempotency check ─────────────────────────────────────────
        if await self._db.event_exists(packet.event.device_event_id):
            logger.info({**ctx, "action": "duplicate_discarded"})
            return await self._reject(truck_id, raw_json, priority_score, "duplicate")

        # ── Step 6: Postgres write ────────────────────────────────────────────
        await self._db.insert_event(packet)

        # ── Step 7: Transform + push to processed queue ───────────────────────
        trip_event      = self._transformer.transform(packet)
        trip_event_json = trip_event.model_dump_json()

        self._redis.push_to_processed(truck_id, trip_event_json, priority_score)

        logger.info({
            **ctx,
            "action":   "event_processed",
            "priority": priority_score,
            "source":   packet.source.value,
            "queue":    RedisSchema.Telemetry.processed(truck_id),
        })

        return IngestionResult(trip_event=trip_event)

    async def run_worker(
        self,
        truck_id:         str,
        poll_interval_ms: int = 100,
    ) -> None:
        """
        Continuous worker loop.
        Polls raw buffer, processes each event, routes to processed/DLQ.
        Runs until cancelled.

        Args:
            truck_id:         truck to watch
            poll_interval_ms: sleep between empty polls (default 100ms)
        """
        raw_key = RedisSchema.Telemetry.buffer(truck_id)

        logger.info({
            "action":   "worker_started",
            "truck_id": truck_id,
            "watching": raw_key,
        })

        while True:
            result = self._redis.pop_from_buffer(raw_key)

            if result is None:
                await asyncio.sleep(poll_interval_ms / 1000)
                continue

            raw_dict, _score = result
            raw_json         = json.dumps(raw_dict)

            await self.process(
                raw      = raw_dict,
                truck_id = truck_id,
                raw_json = raw_json,
            )

    # ── PRIVATE ───────────────────────────────────────────────────────────────

    async def _reject(
        self,
        truck_id:       str,
        raw_json:       str,
        priority_score: int,
        reason:         str,
    ) -> IngestionResult:
        """
        Routes a failed event to the Dead Letter Queue.
        DLQ entry includes the raw payload and structured reason code.
        TTL: 48h (fleet admin inspection window).
        """
        self._redis.push_to_dlq(
            truck_id   = truck_id,
            raw_packet = raw_json,
            reason     = reason,
            priority   = priority_score,
        )
        logger.warning({
            "action": "event_rejected",
            "reason": reason,
            "dlq":    RedisSchema.Telemetry.rejected(truck_id),
        })
        return IngestionResult(rejected=True, reason=reason)

    def _validate_schema(self, raw: dict) -> TelemetryPacket | None:
        try:
            return TelemetryPacket(**raw)
        except (ValidationError, TypeError, KeyError) as e:
            logger.warning({
                "action": "schema_validation_failed",
                "error":  str(e)[:300],
            })
            return None

    def _check_event_matrix(
        self,
        packet: TelemetryPacket,
        ctx:    dict,
    ) -> bool:
        config = EVENT_MATRIX.get(packet.event.event_type)
        if config is None:
            logger.warning({**ctx, "action": "unknown_event_type"})
            return False

        if packet.event.priority != config.priority:
            logger.info({
                **ctx,
                "action":            "priority_override",
                "device_priority":   packet.event.priority,
                "governed_priority": config.priority,
            })
            packet.event.priority = config.priority

        return True

    def _scrub_pii(self, packet: TelemetryPacket) -> TelemetryPacket:
        packet.event.driver_id = self._scrubber.anonymise_driver_id(
            packet.event.driver_id
        )
        if packet.event.location:
            lat, lon = self._scrubber.scrub_location(
                packet.event.location.lat,
                packet.event.location.lon,
            )
            packet.event.location.lat = lat
            packet.event.location.lon = lon

        packet.event.details = self._scrubber.scrub_details(
            packet.event.details,
            packet.event.event_type,
        )
        return packet
