from unittest.mock import AsyncMock, MagicMock

import pytest

from common.db.repositories.scoring_repo import ScoringRepository


@pytest.mark.asyncio
async def test_write_trip_score_uses_trip_upsert():
    repo = ScoringRepository(MagicMock())
    repo._execute_write_scalar = AsyncMock(return_value="score-123")

    out = await repo.write_trip_score(
        trip_id="TRIP-1",
        driver_id="DRV-1",
        score=91.5,
        score_breakdown={"jerk_component": 40.0},
    )

    assert out == "score-123"
    sql = repo._execute_write_scalar.call_args[0][0]
    assert "ON CONFLICT (trip_id) DO UPDATE" in sql


@pytest.mark.asyncio
async def test_write_shap_and_fairness_use_trip_upsert():
    repo = ScoringRepository(MagicMock())
    repo._execute_write = AsyncMock()

    await repo.write_shap_explanations(
        score_id="s-1",
        trip_id="TRIP-1",
        explanations={"top": ["jerk_mean_avg"]},
    )
    await repo.write_fairness_audit(
        score_id="s-1",
        trip_id="TRIP-1",
        driver_id="DRV-1",
        audit_result={"bias_detected": False},
    )

    shap_sql = repo._execute_write.call_args_list[0][0][0]
    fairness_sql = repo._execute_write.call_args_list[1][0][0]
    assert "ON CONFLICT (trip_id) DO UPDATE" in shap_sql
    assert "ON CONFLICT (trip_id) DO UPDATE" in fairness_sql
