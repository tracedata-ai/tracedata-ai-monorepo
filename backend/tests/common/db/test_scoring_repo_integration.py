from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import text

from common.db.engine import engine
from common.db.repositories.scoring_repo import ScoringRepository

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_scoring_repo_upsert_is_one_row_per_trip():
    # Skip cleanly when integration DB isn't available.
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - environment-dependent
        pytest.skip(f"Postgres unavailable for integration test: {exc}")

    repo = ScoringRepository(engine)
    trip_id = f"TRP-IT-{uuid4().hex[:10]}"
    driver_id = "DRV-IT-001"

    score_id_1 = await repo.write_trip_score(
        trip_id=trip_id,
        driver_id=driver_id,
        score=81.0,
        score_breakdown={"jerk_component": 30.0},
    )
    await repo.write_shap_explanations(
        score_id=score_id_1,
        trip_id=trip_id,
        explanations={"narrative": "first"},
    )
    await repo.write_fairness_audit(
        score_id=score_id_1,
        trip_id=trip_id,
        driver_id=driver_id,
        audit_result={"bias_detected": False},
    )

    score_id_2 = await repo.write_trip_score(
        trip_id=trip_id,
        driver_id=driver_id,
        score=92.0,
        score_breakdown={"jerk_component": 40.0},
    )
    await repo.write_shap_explanations(
        score_id=score_id_2,
        trip_id=trip_id,
        explanations={"narrative": "second"},
    )
    await repo.write_fairness_audit(
        score_id=score_id_2,
        trip_id=trip_id,
        driver_id=driver_id,
        audit_result={"bias_detected": False, "updated": True},
    )

    async with engine.connect() as conn:
        trip_scores = await conn.execute(
            text(
                "SELECT COUNT(*) FROM scoring_schema.trip_scores WHERE trip_id = :trip_id"
            ),
            {"trip_id": trip_id},
        )
        shap_rows = await conn.execute(
            text(
                "SELECT COUNT(*) FROM scoring_schema.shap_explanations WHERE trip_id = :trip_id"
            ),
            {"trip_id": trip_id},
        )
        fairness_rows = await conn.execute(
            text(
                "SELECT COUNT(*) FROM scoring_schema.fairness_audit WHERE trip_id = :trip_id"
            ),
            {"trip_id": trip_id},
        )
        updated_score = await conn.execute(
            text("SELECT score FROM scoring_schema.trip_scores WHERE trip_id = :trip_id"),
            {"trip_id": trip_id},
        )
        updated_shap = await conn.execute(
            text(
                "SELECT explanations FROM scoring_schema.shap_explanations WHERE trip_id = :trip_id"
            ),
            {"trip_id": trip_id},
        )

    assert int(trip_scores.scalar_one()) == 1
    assert int(shap_rows.scalar_one()) == 1
    assert int(fairness_rows.scalar_one()) == 1
    assert float(updated_score.scalar_one()) == 92.0
    assert "second" in str(updated_shap.scalar_one())

    # Best-effort cleanup for this integration key.
    async with engine.begin() as conn:
        await conn.execute(
            text("DELETE FROM scoring_schema.fairness_audit WHERE trip_id = :trip_id"),
            {"trip_id": trip_id},
        )
        await conn.execute(
            text("DELETE FROM scoring_schema.shap_explanations WHERE trip_id = :trip_id"),
            {"trip_id": trip_id},
        )
        await conn.execute(
            text("DELETE FROM scoring_schema.trip_scores WHERE trip_id = :trip_id"),
            {"trip_id": trip_id},
        )
