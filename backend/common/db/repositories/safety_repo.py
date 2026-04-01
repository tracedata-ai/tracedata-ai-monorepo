"""
SAFETY AGENT REPOSITORY — Write tables owned by SafetyAgent only.

Layer 1 Enforcement:
  SafetyAgent receives ONLY this repo → impossible to write to other schemas
"""

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
        analysis: dict,
    ) -> None:
        """Write harsh event analysis to safety_schema."""
        await self._execute_write(
            """
                    INSERT INTO safety_schema.harsh_events_analysis
                    (event_id, trip_id, event_type, severity, analysis, created_at)
                    VALUES (:event_id, :trip_id, :event_type, :severity, :analysis, :now)
                """,
            {
                "event_id": event_id,
                "trip_id": trip_id,
                "event_type": event_type,
                "severity": severity,
                "analysis": analysis,
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
    ) -> str:
        """Write safety decision; returns decision_id."""
        return await self._execute_write_scalar(
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
