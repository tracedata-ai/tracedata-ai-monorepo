"""
Packet Transformer — flattens TelemetryPacket → TripEvent.

TelemetryPacket is the nested device/app format optimised for transmission.
TripEvent is the flat agent format — every field directly accessible.

At this point the packet has already been:
  1. Schema validated      (Pydantic)
  2. EVENT_MATRIX checked  (governance)
  3. Injection scanned     (OWASP LLM01)
  4. PII scrubbed          (OWASP LLM02)

The transformer is purely structural — no validation, no decisions.

Location: backend/core/ingestion/transformer.py
"""

import logging
from datetime import UTC, datetime

from common.config.events import EVENT_MATRIX
from common.models.events import TelemetryPacket, TripEvent

logger = logging.getLogger(__name__)


class PacketTransformer:
    """
    Stateless transformer. Safe to reuse across requests.
    Input:  PII-scrubbed TelemetryPacket
    Output: flat TripEvent ready for the processed queue
    """

    def transform(self, packet: TelemetryPacket) -> TripEvent:
        """
        Converts a validated, scrubbed TelemetryPacket into a flat TripEvent.
        Resolves category and numeric priority from EVENT_MATRIX.
        """
        event = packet.event
        config = EVENT_MATRIX[event.event_type]

        return TripEvent(
            # ── Correlation IDs ────────────────────────────────────────────
            event_id=event.event_id,
            device_event_id=event.device_event_id,
            trip_id=event.trip_id,
            # ── Identity (anonymised before this point) ────────────────────
            driver_id=event.driver_id,  # DRV-ANON-XXXX at this stage
            truck_id=event.truck_id,
            # ── Classification (governed by EVENT_MATRIX) ──────────────────
            event_type=event.event_type,
            category=config.category,
            priority=event.priority,
            # ── Temporal anchor ────────────────────────────────────────────
            timestamp=event.timestamp,
            offset_seconds=event.offset_seconds,
            # ── Spatial anchor ─────────────────────────────────────────────
            trip_meter_km=event.trip_meter_km,
            odometer_km=event.odometer_km,
            location=event.location,
            # ── Content ────────────────────────────────────────────────────
            details=event.details,
            evidence=packet.evidence,
            # ── Routing metadata ───────────────────────────────────────────
            source=packet.source,
            ping_type=packet.ping_type,
            is_emergency=packet.is_emergency,
            # ── Processing metadata ────────────────────────────────────────
            ingested_at=datetime.now(UTC),
        )
