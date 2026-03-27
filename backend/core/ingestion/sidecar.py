from typing import Any

from common.config.events import PRIORITY_MAP
from common.db.engine import AsyncSessionLocal
from common.models.events import TelemetryPacket, TripEvent
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

from .db import IngestionDB
from .injection import InjectionScanner
from security.pii import PIIScrubber
from .transformer import PacketTransformer


class IngestionSidecar:
    """
    The 7-Step Security Boundary Orchestrator.
    Transforms raw TelemetryPacket into clean TripEvent.
    """

    def __init__(self, redis: RedisClient):
        self.redis = redis
        self.scanner = InjectionScanner()
        self.scrubber = PIIScrubber()
        self.transformer = PacketTransformer()
        self.db = IngestionDB()

    async def process_packet(self, raw_packet: dict) -> bool:
        """
        Executes the 7-step ingestion pipeline.
        Returns True if success, False if rejected.
        """
        truck_id = raw_packet.get("event", {}).get("truck_id", "unknown")

        try:
            # 1. Schema Validation
            packet = TelemetryPacket(**raw_packet)

            # 2. Matrix Check & Transformation (Governance)
            # This step also validates that event_type exists in MATRIX
            event = self.transformer.to_trip_event(packet)

            # 3. Injection Scan (OWASP LLM01)
            if self.scanner.scan_payload(raw_packet):
                await self._reject(truck_id, raw_packet, "injection_detected")
                return False

            # 4. PII Scrub (OWASP LLM02)
            # We preserve the REAL driver_id for Postgres, but agents get the ANON version.
            real_driver_id = event.driver_id
            
            # Anonymize Driver ID
            event.driver_id = self.scrubber.anonymise_driver_id(real_driver_id)
            
            # Round Location
            if event.location:
                event.location.lat, event.location.lon = self.scrubber.scrub_location(
                    event.location.lat, event.location.lon
                )
            
            # Mask sensitive Details
            event.details = self.scrubber.scrub_details(event.details, event.event_type)

            # 5. Idempotency & 6. DB Write 1
            async with AsyncSessionLocal() as session:
                if await self.db.event_exists(session, event.device_event_id):
                    # Already ingested, silent discard (success=True but no route)
                    return True

                # IMPORTANT: IngestionDB.save_event expects the version it saves to DB
                # In this architecture, we save the CLEAN (anonymized/scrubbed) version
                # as the source of truth for the rest of the system.
                await self.db.save_event(session, event)

            # 7. ROUTE: Success
            processed_key = RedisSchema.Telemetry.processed(truck_id)
            score = PRIORITY_MAP.get(event.priority, 9)
            await self.redis.push_to_processed(
                processed_key, event.model_dump_json(), score
            )

            return True

        except Exception as e:
            # Step 7b: FAILURE -> Rejected Queue (DLQ)
            await self._reject(truck_id, raw_packet, str(e))
            return False

    async def _reject(self, truck_id: str, raw_packet: dict, reason: str):
        """Pushes rejected packet to DLQ."""
        rejected_key = RedisSchema.Telemetry.rejected(truck_id)
        # Wrap packet with rejection reason
        payload = {
            "reason": reason,
            "packet": raw_packet,
        }
        import json

        await self.redis.push_to_rejected(
            rejected_key,
            json.dumps(payload),
            score=0,  # CRITICAL for inspection
            ttl=RedisSchema.Telemetry.DLQ_TTL,
        )
