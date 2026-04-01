"""
SCORING AGENT REPOSITORY — Write tables owned by ScoringAgent only.

Layer 1 Enforcement:
  ScoringAgent receives ONLY this repo → impossible to write to other schemas
"""

from typing import Any

from common.db.schema_repository import SchemaRepository


class ScoringRepository(SchemaRepository):
    """ScoringAgent's write operations on owned tables."""

    async def write_trip_score(
        self,
        trip_id: str,
        driver_id: str,
        score: float,
        score_breakdown: dict,
    ) -> str:
        """Write trip score; returns score_id."""
        return await self._execute_write_scalar(
            """
                    INSERT INTO scoring_schema.trip_scores
                    (trip_id, driver_id, score, score_breakdown, created_at)
                    VALUES (:trip_id, :driver_id, :score, :breakdown, :now)
                    RETURNING score_id
                """,
            {
                "trip_id": trip_id,
                "driver_id": driver_id,
                "score": score,
                "breakdown": score_breakdown,
            },
        )

    async def write_shap_explanations(
        self,
        score_id: str,
        trip_id: str,
        explanations: dict,
    ) -> None:
        """Write SHAP explanations for a score."""
        await self._execute_write(
            """
                    INSERT INTO scoring_schema.shap_explanations
                    (score_id, trip_id, explanations, created_at)
                    VALUES (:score_id, :trip_id, :explanations, :now)
                """,
            {
                "score_id": score_id,
                "trip_id": trip_id,
                "explanations": explanations,
            },
        )

    async def write_fairness_audit(
        self,
        score_id: str,
        trip_id: str,
        driver_id: str,
        audit_result: dict,
    ) -> None:
        """Write fairness audit for a score."""
        await self._execute_write(
            """
                    INSERT INTO scoring_schema.fairness_audit
                    (score_id, trip_id, driver_id, audit_result, created_at)
                    VALUES (:score_id, :trip_id, :driver_id, :audit_result, :now)
                """,
            {
                "score_id": score_id,
                "trip_id": trip_id,
                "driver_id": driver_id,
                "audit_result": audit_result,
            },
        )

    async def get_trip_score(
        self,
        score_id: str,
    ) -> dict[str, Any] | None:
        """Read own score (for validation)."""
        return await self._fetch_one_mapping(
            """
                    SELECT * FROM scoring_schema.trip_scores
                    WHERE score_id = :score_id
                """,
            {"score_id": score_id},
        )
