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


def _parse_json_field(value: Any) -> dict[str, Any]:
    """Handle JSONB values returned as dict or JSON string."""
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        return json.loads(value)
    return {}


def _safe_parse_json_object(value: Any) -> dict[str, Any]:
    """Like _parse_json_field but never raises (empty dict on failure)."""
    try:
        return _parse_json_field(value)
    except (json.JSONDecodeError, TypeError, ValueError):
        return {}


def _location_and_evidence_for_event_row(
    lat: Any,
    lon: Any,
    evidence_video_url: Any,
    evidence_voice_url: Any,
    evidence_sensor_url: Any,
    raw_payload: Any,
) -> tuple[dict[str, float] | None, dict[str, Any]]:
    """
    Build location {lat, lon} and evidence URLs/metadata for cache warming / agents.

    Prefer DB columns; fall back to TelemetryPacket JSON in raw_payload (event.location,
    top-level evidence block). Column URLs override packet fields when both exist.
    """
    location: dict[str, float] | None = None
    if lat is not None and lon is not None:
        try:
            location = {"lat": float(lat), "lon": float(lon)}
        except (TypeError, ValueError):
            location = None

    pkg = _safe_parse_json_object(raw_payload)

    if location is None:
        ev_nested = pkg.get("event") if isinstance(pkg, dict) else None
        if isinstance(ev_nested, dict):
            loc = ev_nested.get("location")
            if isinstance(loc, dict):
                try:
                    la = loc.get("lat") if loc.get("lat") is not None else loc.get("latitude")
                    lo = loc.get("lon") if loc.get("lon") is not None else loc.get("longitude")
                    if la is not None and lo is not None:
                        location = {"lat": float(la), "lon": float(lo)}
                except (TypeError, ValueError):
                    pass

    evidence: dict[str, Any] = {}
    pkg_ev = pkg.get("evidence") if isinstance(pkg, dict) else None
    if isinstance(pkg_ev, dict):
        for k, v in pkg_ev.items():
            if v is not None:
                evidence[k] = v

    if evidence_video_url:
        evidence["video_url"] = evidence_video_url
    if evidence_voice_url:
        evidence["voice_url"] = evidence_voice_url
    if evidence_sensor_url:
        evidence["sensor_dump_url"] = evidence_sensor_url

    return location, evidence


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
                        details,
                        priority AS severity,
                        lat,
                        lon,
                        evidence_video_url,
                        evidence_voice_url,
                        evidence_sensor_url,
                        raw_payload
                    FROM pipeline_events
                    WHERE event_id = :event_id
                """),
                {"event_id": event_id},
            )
            row = result.mappings().first()
            if not row:
                return None

            details = row["details"]
            location, evidence = _location_and_evidence_for_event_row(
                row["lat"],
                row["lon"],
                row["evidence_video_url"],
                row["evidence_voice_url"],
                row["evidence_sensor_url"],
                row["raw_payload"],
            )

            return {
                "event_id": row["event_id"],
                "trip_id": row["trip_id"],
                "event_type": row["event_type"],
                "device_event_id": row["device_event_id"],
                "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
                "data": _parse_json_field(details),
                "severity": row["severity"],
                "location": location,
                "evidence": evidence,
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
        row = None
        try:
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
        except Exception:
            # E2E bootstrap schema uses pipeline_trips/route_type.
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
                            route_type AS route_name
                        FROM pipeline_trips
                        WHERE trip_id = :trip_id
                    """),
                    {"trip_id": trip_id},
                )
                row = result.first()

        if not row:
            # Last-resort fallback when trip lifecycle table is missing/not populated.
            async with self._engine.connect() as conn:
                result = await conn.execute(
                    text("""
                        SELECT
                            trip_id,
                            MIN(driver_id) AS driver_id,
                            MIN(truck_id) AS truck_id,
                            MIN(timestamp) AS started_at,
                            MAX(timestamp) AS ended_at,
                            NULL::double precision AS distance_km,
                            NULL::integer AS duration_minutes,
                            'active' AS status,
                            NULL::varchar AS route_name
                        FROM pipeline_events
                        WHERE trip_id = :trip_id
                        GROUP BY trip_id
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
                        details,
                        priority AS severity,
                        lat,
                        lon,
                        evidence_video_url,
                        evidence_voice_url,
                        evidence_sensor_url,
                        raw_payload
                    FROM pipeline_events
                    WHERE trip_id = :trip_id
                    ORDER BY timestamp ASC
                """),
                {"trip_id": trip_id},
            )
            rows = result.mappings().fetchall()

            if not rows:
                return []

            pings = []
            for row in rows:
                location, evidence = _location_and_evidence_for_event_row(
                    row["lat"],
                    row["lon"],
                    row["evidence_video_url"],
                    row["evidence_voice_url"],
                    row["evidence_sensor_url"],
                    row["raw_payload"],
                )
                pings.append(
                    {
                        "event_id": row["event_id"],
                        "trip_id": row["trip_id"],
                        "event_type": row["event_type"],
                        "device_event_id": row["device_event_id"],
                        "timestamp": row["timestamp"].isoformat()
                        if row["timestamp"]
                        else None,
                        "data": _parse_json_field(row["details"]),
                        "severity": row["severity"],
                        "location": location,
                        "evidence": evidence,
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
                    SELECT AVG(score) AS avg_score
                    FROM (
                        SELECT score
                        FROM scoring_schema.trip_scores
                        WHERE driver_id = :driver_id
                        ORDER BY created_at DESC
                        LIMIT :n
                    ) recent_scores
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

    async def insert_synthetic_received_event(
        self,
        *,
        device_event_id: str,
        event_id: str,
        trip_id: str,
        truck_id: str,
        driver_id: str,
        event_type: str,
        category: str,
        priority: str,
        timestamp: datetime,
        details: dict[str, Any] | None = None,
    ) -> bool:
        """
        Insert a pipeline_events row for an orchestrator-emitted follow-up.

        Row starts as status='received' so acquire_lock can claim it.
        """
        now = datetime.now(UTC).replace(tzinfo=None)
        ts = timestamp.replace(tzinfo=None) if timestamp.tzinfo else timestamp
        payload_hint = json.dumps({"synthetic": True, "event_type": event_type})
        detail_blob = json.dumps(details or {})

        async with self._engine.begin() as conn:
            result = await conn.execute(
                text("""
                    INSERT INTO pipeline_events (
                        device_event_id,
                        event_id,
                        trip_id,
                        driver_id,
                        truck_id,
                        event_type,
                        category,
                        priority,
                        ping_type,
                        source,
                        is_emergency,
                        timestamp,
                        offset_seconds,
                        trip_meter_km,
                        odometer_km,
                        lat,
                        lon,
                        details,
                        raw_payload,
                        status,
                        retry_count,
                        ingested_at
                    ) VALUES (
                        :device_event_id,
                        :event_id,
                        :trip_id,
                        :driver_id,
                        :truck_id,
                        :event_type,
                        :category,
                        :priority,
                        NULL,
                        NULL,
                        false,
                        :timestamp,
                        0,
                        NULL,
                        NULL,
                        NULL,
                        NULL,
                        CAST(:details AS jsonb),
                        :raw_payload,
                        'received',
                        0,
                        :ingested_at
                    )
                    ON CONFLICT (device_event_id) DO NOTHING
                """),
                {
                    "device_event_id": device_event_id,
                    "event_id": event_id,
                    "trip_id": trip_id,
                    "driver_id": driver_id,
                    "truck_id": truck_id,
                    "event_type": event_type,
                    "category": category,
                    "priority": priority,
                    "timestamp": ts,
                    "details": detail_blob,
                    "raw_payload": payload_hint,
                    "ingested_at": now,
                },
            )
            inserted = result.rowcount == 1 if result.rowcount is not None else False
        if inserted:
            logger.info(
                {
                    "action": "synthetic_event_inserted",
                    "device_event_id": device_event_id,
                    "trip_id": trip_id,
                    "event_type": event_type,
                }
            )
        return inserted
