"""
PII Scrubber — OWASP LLM02:2025 mitigation.

Anonymises sensitive fields before TripEvent enters the agent pipeline:
  driver_id    → deterministic hash token (DRV-ANON-XXXXXXXX)
  GPS lat/lon  → rounded to 2dp (~1km precision)
  injury data  → masked for non-Safety event types

The REAL driver_id is preserved only in the Postgres events table
for compliance and audit. It never reaches agents or LLM calls.

Anonymisation is deterministic — the same real_id always maps to
the same token within a deployment (salt-bound). This allows
cross-event correlation (same driver, multiple trips) without
exposing the real identity.

Location: backend/security/pii.py
"""

import copy
import hashlib
import logging
import os

logger = logging.getLogger(__name__)

# Event types where injury_severity_estimate is legitimately needed
_SAFETY_EVENT_TYPES = frozenset({"collision", "rollover", "driver_sos"})

# GPS precision — 2dp = ~1.1km at equator
_GPS_PRECISION = 2

# Cache size cap — prevents unbounded growth in long-running workers
# 300 trucks × ~5 drivers each = 1500 max in practice
_CACHE_MAX = 10_000


class PIIScrubber:
    """
    Scrubs PII from TelemetryPacket fields before pipeline entry.

    Maintains an in-process cache of real_id → anon_id mappings
    for the lifetime of the process. Cache is capped at _CACHE_MAX
    entries (FIFO eviction) to prevent unbounded memory growth.
    """

    def __init__(self) -> None:
        self._salt: str = os.getenv("PII_SALT", "tracedata-default-salt")
        self._cache: dict[str, str] = {}

    # ── PUBLIC ────────────────────────────────────────────────────────────────

    def anonymise_driver_id(self, real_driver_id: str) -> str:
        """
        Returns a deterministic anonymous token for the real driver_id.
        Format: DRV-ANON-{8 hex chars uppercase}
        Example: DRV-ANON-3F7A9C12

        The real_driver_id is NOT stored here. The caller (IngestionDB)
        retains the original for the Postgres audit write.
        """
        if real_driver_id not in self._cache:
            if len(self._cache) >= _CACHE_MAX:
                # Evict oldest entry — FIFO via dict insertion order (Python 3.7+)
                oldest = next(iter(self._cache))
                del self._cache[oldest]
                logger.debug(
                    {
                        "action": "pii_cache_eviction",
                        "evicted": oldest[:4] + "****",  # log only prefix, not full id
                    }
                )
            token = self._hash(real_driver_id)
            self._cache[real_driver_id] = f"DRV-ANON-{token}"

        return self._cache[real_driver_id]

    def scrub_location(
        self,
        lat: float | None,
        lon: float | None,
    ) -> tuple[float | None, float | None]:
        """
        Rounds GPS coordinates to 2dp (~1km precision).
        Returns (None, None) if either input is None.
        """
        if lat is None or lon is None:
            return None, None
        return round(lat, _GPS_PRECISION), round(lon, _GPS_PRECISION)

    def scrub_details(
        self,
        details: dict | None,
        event_type: str,
    ) -> dict | None:
        """
        Masks sensitive fields in event details for non-Safety event types.
        injury_severity_estimate is only needed by the Safety Agent.

        Uses deepcopy — event details can contain nested dicts
        (e.g. collision.sub_system data). Shallow copy would mutate
        the original payload in-place.
        """
        if details is None:
            return None

        scrubbed = copy.deepcopy(details)

        if (
            event_type not in _SAFETY_EVENT_TYPES
            and "injury_severity_estimate" in scrubbed
        ):
            scrubbed["injury_severity_estimate"] = "REDACTED"

        return scrubbed

    # ── PRIVATE ───────────────────────────────────────────────────────────────

    def _hash(self, value: str) -> str:
        """
        SHA-256 hash of salt:value, first 8 hex chars uppercase.
        Deterministic within a deployment (same salt).
        Not reversible without the salt.
        """
        digest = hashlib.sha256(f"{self._salt}:{value}".encode()).hexdigest()
        return digest[:8].upper()
