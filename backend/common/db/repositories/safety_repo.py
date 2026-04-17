"""
SAFETY AGENT REPOSITORY — Write tables owned by SafetyAgent only.

Layer 1 Enforcement:
  SafetyAgent receives ONLY this repo → impossible to write to other schemas
"""

import json
from datetime import datetime
from typing import Any

from common.db.schema_repository import SchemaRepository


class SafetyRepository(SchemaRepository):
    """SafetyAgent's write operations on owned tables."""

    async def write_harsh_event_analysis(
        self,
        event_id: str,
        trip_id: str,
        event_type: str,
        severity: str,
        event_timestamp: datetime | None,
        lat: float | None,
        lon: float | None,
        location_name: str | None,
        traffic_conditions: str | None,
        weather_conditions: str | None,
        analysis: dict,
    ) -> None:
        """Write harsh event analysis to safety_schema."""
        await self._execute_write(
            """
                    INSERT INTO safety_schema.harsh_events_analysis
                    (
                      event_id, trip_id, event_type, severity,
                      event_timestamp, lat, lon, location_name,
                      traffic_conditions, weather_conditions,
                      analysis, created_at
                    )
                    VALUES (
                      :event_id, :trip_id, :event_type, :severity,
                      :event_timestamp, :lat, :lon, :location_name,
                      :traffic_conditions, :weather_conditions,
                      :analysis, :now
                    )
                """,
            {
                "event_id": event_id,
                "trip_id": trip_id,
                "event_type": event_type,
                "severity": severity,
                "event_timestamp": event_timestamp,
                "lat": lat,
                "lon": lon,
                "location_name": location_name,
                "traffic_conditions": traffic_conditions,
                "weather_conditions": weather_conditions,
                "analysis": json.dumps(analysis),
            },
        )

    async def write_safety_decision(
        self,
        event_id: str,
        trip_id: str,
        decision: str,
        action: str,
        reason: str,
        recommended_action: str | None = None,
        driver_id: str | None = None,
    ) -> str:
        """Write safety decision; returns decision_id."""
        decision_id = await self._execute_write_scalar(
            """
                    INSERT INTO safety_schema.safety_decisions
                    (event_id, trip_id, decision, action, reason, recommended_action, created_at)
                    VALUES (:event_id, :trip_id, :decision, :action, :reason, :rec_action, :now)
                    RETURNING decision_id
                """,
            {
                "event_id": event_id,
                "trip_id": trip_id,
                "decision": decision,
                "action": action,
                "reason": reason,
                "rec_action": recommended_action,
            },
        )
        embed_content = f"Safety decision: {decision}. Action: {action}. Reason: {reason}"
        if recommended_action:
            embed_content += f" Recommended: {recommended_action}"
        await self._store_embedding("safety_decision", event_id, embed_content, driver_id, trip_id)
        return decision_id

    async def get_harsh_event_analysis(
        self,
        event_id: str,
    ) -> dict[str, Any] | None:
        """Read own analysis (for validation)."""
        return await self._fetch_one_mapping(
            """
                    SELECT * FROM safety_schema.harsh_events_analysis
                    WHERE event_id = :event_id
                """,
            {"event_id": event_id},
        )
