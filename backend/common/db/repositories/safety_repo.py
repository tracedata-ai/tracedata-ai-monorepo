"""
SAFETY AGENT REPOSITORY — Write tables owned by SafetyAgent only.

Layer 1 Enforcement:
  SafetyAgent receives ONLY this repo → impossible to write to other schemas
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


class SafetyRepository:
    """SafetyAgent's write operations on owned tables."""

    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def write_harsh_event_analysis(
        self,
        event_id: str,
        trip_id: str,
        event_type: str,
        severity: str,
        analysis: dict,
    ) -> None:
        """Write harsh event analysis to safety_schema.

        Owned table: safety_schema.harsh_events_analysis
        """
        async with self._engine.begin() as conn:
            await conn.execute(
                text(
                    """
                    INSERT INTO safety_schema.harsh_events_analysis
                    (event_id, trip_id, event_type, severity, analysis, created_at)
                    VALUES (:event_id, :trip_id, :event_type, :severity, :analysis, :now)
                """
                ),
                {
                    "event_id": event_id,
                    "trip_id": trip_id,
                    "event_type": event_type,
                    "severity": severity,
                    "analysis": analysis,
                    "now": datetime.now(UTC).replace(tzinfo=None),
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
        """Write safety decision for an event.

        Owned table: safety_schema.safety_decisions

        Returns:
            Decision ID
        """
        async with self._engine.begin() as conn:
            result = await conn.execute(
                text(
                    """
                    INSERT INTO safety_schema.safety_decisions
                    (event_id, trip_id, decision, action, reason, recommended_action, created_at)
                    VALUES (:event_id, :trip_id, :decision, :action, :reason, :rec_action, :now)
                    RETURNING decision_id
                """
                ),
                {
                    "event_id": event_id,
                    "trip_id": trip_id,
                    "decision": decision,
                    "action": action,
                    "reason": reason,
                    "rec_action": recommended_action,
                    "now": datetime.now(UTC).replace(tzinfo=None),
                },
            )
            decision_id = result.scalar()
            return decision_id

    async def get_harsh_event_analysis(
        self,
        event_id: str,
    ) -> dict[str, Any] | None:
        """Read own analysis (for validation)."""
        async with self._engine.connect() as conn:
            result = await conn.execute(
                text(
                    """
                    SELECT * FROM safety_schema.harsh_events_analysis
                    WHERE event_id = :event_id
                """
                ),
                {"event_id": event_id},
            )
            row = result.first()
            return dict(row._mapping) if row else None
