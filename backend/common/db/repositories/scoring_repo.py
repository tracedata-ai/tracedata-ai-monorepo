"""
SCORING AGENT REPOSITORY — Write tables owned by ScoringAgent only.

Layer 1 Enforcement:
  ScoringAgent receives ONLY this repo → impossible to write to other schemas
"""

import json
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
                    ON CONFLICT (trip_id) DO UPDATE
                    SET
                        driver_id = EXCLUDED.driver_id,
                        score = EXCLUDED.score,
                        score_breakdown = EXCLUDED.score_breakdown,
                        created_at = EXCLUDED.created_at
                    RETURNING score_id
                """,
            {
                "trip_id": trip_id,
                "driver_id": driver_id,
                "score": score,
                "breakdown": json.dumps(score_breakdown),
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
                    ON CONFLICT (trip_id) DO UPDATE
                    SET
                        score_id = EXCLUDED.score_id,
                        explanations = EXCLUDED.explanations,
                        created_at = EXCLUDED.created_at
                """,
            {
                "score_id": score_id,
                "trip_id": trip_id,
                "explanations": json.dumps(explanations),
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
                    ON CONFLICT (trip_id) DO UPDATE
                    SET
                        score_id = EXCLUDED.score_id,
                        driver_id = EXCLUDED.driver_id,
                        audit_result = EXCLUDED.audit_result,
                        created_at = EXCLUDED.created_at
                """,
            {
                "score_id": score_id,
                "trip_id": trip_id,
                "driver_id": driver_id,
                "audit_result": json.dumps(audit_result),
            },
        )

    async def write_scoring_narrative(
        self,
        score_id: str,
        narrative: str,
        driver_id: str | None = None,
        trip_id: str | None = None,
    ) -> None:
        """Attach LLM-generated human-readable narrative to an existing trip score row."""
        await self._execute_write(
            """
                    UPDATE scoring_schema.trip_scores
                    SET scoring_narrative = :narrative
                    WHERE score_id = :score_id
                """,
            {"score_id": score_id, "narrative": narrative},
        )
        await self._store_embedding(
            "scoring_narrative", str(score_id), narrative, driver_id, trip_id
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
