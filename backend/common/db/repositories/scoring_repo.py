"""
SCORING AGENT REPOSITORY — Write tables owned by ScoringAgent only.

Layer 1 Enforcement:
  ScoringAgent receives ONLY this repo → impossible to write to other schemas
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


class ScoringRepository:
    """ScoringAgent's write operations on owned tables."""

    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def write_trip_score(
        self,
        trip_id: str,
        driver_id: str,
        score: float,
        score_breakdown: dict,
    ) -> str:
        """Write trip score to scoring_schema.

        Owned table: scoring_schema.trip_scores

        Returns:
            Score ID
        """
        async with self._engine.begin() as conn:
            result = await conn.execute(
                text(
                    """
                    INSERT INTO scoring_schema.trip_scores
                    (trip_id, driver_id, score, score_breakdown, created_at)
                    VALUES (:trip_id, :driver_id, :score, :breakdown, :now)
                    RETURNING score_id
                """
                ),
                {
                    "trip_id": trip_id,
                    "driver_id": driver_id,
                    "score": score,
                    "breakdown": score_breakdown,
                    "now": datetime.now(UTC).replace(tzinfo=None),
                },
            )
            score_id = result.scalar()
            return score_id

    async def write_shap_explanations(
        self,
        score_id: str,
        trip_id: str,
        explanations: dict,
    ) -> None:
        """Write SHAP explanations for a score.

        Owned table: scoring_schema.shap_explanations
        """
        async with self._engine.begin() as conn:
            await conn.execute(
                text(
                    """
                    INSERT INTO scoring_schema.shap_explanations
                    (score_id, trip_id, explanations, created_at)
                    VALUES (:score_id, :trip_id, :explanations, :now)
                """
                ),
                {
                    "score_id": score_id,
                    "trip_id": trip_id,
                    "explanations": explanations,
                    "now": datetime.now(UTC).replace(tzinfo=None),
                },
            )

    async def write_fairness_audit(
        self,
        score_id: str,
        trip_id: str,
        driver_id: str,
        audit_result: dict,
    ) -> None:
        """Write fairness audit for a score.

        Owned table: scoring_schema.fairness_audit
        """
        async with self._engine.begin() as conn:
            await conn.execute(
                text(
                    """
                    INSERT INTO scoring_schema.fairness_audit
                    (score_id, trip_id, driver_id, audit_result, created_at)
                    VALUES (:score_id, :trip_id, :driver_id, :audit_result, :now)
                """
                ),
                {
                    "score_id": score_id,
                    "trip_id": trip_id,
                    "driver_id": driver_id,
                    "audit_result": audit_result,
                    "now": datetime.now(UTC).replace(tzinfo=None),
                },
            )

    async def get_trip_score(
        self,
        score_id: str,
    ) -> dict[str, Any] | None:
        """Read own score (for validation)."""
        async with self._engine.connect() as conn:
            result = await conn.execute(
                text(
                    """
                    SELECT * FROM scoring_schema.trip_scores
                    WHERE score_id = :score_id
                """
                ),
                {"score_id": score_id},
            )
            row = result.first()
            return dict(row._mapping) if row else None
