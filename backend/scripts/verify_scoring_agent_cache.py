"""
Populate orchestrator-style Redis keys and run ScoringAgent with a mocked LangGraph.

Proves the agent reads all_pings, historical_avg, trip_context and invokes the graph.

Usage (from backend/):
  REDIS_URL=redis://localhost:6379/0 python scripts/verify_scoring_agent_cache.py
"""

import asyncio
import json
import os
import sys
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

# Pydantic settings read env at first load — set before any backend imports.
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
os.environ["REDIS_URL"] = REDIS_URL

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.scoring.agent import ScoringAgent
from common.db.engine import engine
from common.models.security import IntentCapsule, ScopedToken
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema
from common.samples.smoothness_batch import smoothness_details_mild_variant
from langchain_core.messages import AIMessage


async def main() -> None:
    trip_id = "TRIP-VERIFY-SCORING"

    redis_client = RedisClient()

    pings_key = RedisSchema.Trip.agent_data(trip_id, "scoring", "all_pings")
    avg_key = RedisSchema.Trip.agent_data(trip_id, "scoring", "historical_avg")
    ctx_key = RedisSchema.Trip.agent_data(trip_id, "scoring", "trip_context")

    all_pings = [
        {
            "event_type": "smoothness_log",
            "details": smoothness_details_mild_variant(0),
        }
    ]
    await redis_client._client.set(pings_key, json.dumps(all_pings))
    await redis_client._client.set(avg_key, json.dumps({"rolling_avg_score": 70.0}))
    await redis_client._client.set(
        ctx_key,
        json.dumps({"trip_id": trip_id, "driver_id": "DRV-VERIFY"}),
    )

    expiry = datetime.now(UTC) + timedelta(hours=1)
    capsule = IntentCapsule(
        trip_id=trip_id,
        agent="scoring",
        priority=3,
        device_event_id="DEV-VERIFY-1",
        token=ScopedToken(
            agent="scoring",
            trip_id=trip_id,
            expires_at=expiry,
            read_keys=[pings_key, avg_key, ctx_key],
            write_keys=[],
        ),
    )

    graph_json = {
        "behaviour_score": 72.5,
        "score_label": "Good",
        "score_breakdown": {
            "jerk_component": 20,
            "speed_component": 18,
            "lateral_component": 17,
            "engine_component": 10,
        },
        "coaching_required": False,
        "coaching_reasons": [],
        "shap_explanation": {"method": "test"},
        "fairness_audit": {
            "demographic_parity": "PASS",
            "equalized_odds": "PASS",
            "bias_detected": False,
            "recommendation": "ok",
        },
    }
    mock_graph = MagicMock()
    mock_graph.ainvoke = AsyncMock(
        return_value={"messages": [AIMessage(content=json.dumps(graph_json))]}
    )

    mock_llm = MagicMock()

    with (
        patch("agents.scoring.agent.build_tool_loop_graph", return_value=mock_graph),
        patch(
            "agents.base.agent.TDAgentBase._release_lock",
            new_callable=AsyncMock,
        ),
    ):
        agent = ScoringAgent(
            engine_param=engine, redis_client=redis_client, llm=mock_llm
        )
        agent.scoring_repo = MagicMock()
        agent.scoring_repo.write_trip_score = AsyncMock(return_value="score-uuid-1")
        agent.scoring_repo.write_shap_explanations = AsyncMock()
        agent.scoring_repo.write_fairness_audit = AsyncMock()
        result = await agent.run(capsule.model_dump(mode="json"))

    await redis_client._client.aclose()

    print("run result:", json.dumps(result, indent=2, default=str))
    assert result.get("status") == "success", result
    assert mock_graph.ainvoke.called, "graph.ainvoke should have been called"
    ca = mock_graph.ainvoke.call_args
    assert ca is not None
    state = ca.args[0] if ca.args else {}
    msgs = state.get("messages") or []
    assert len(msgs) >= 2, "expected system + human messages"
    human = msgs[1]
    user_content = getattr(human, "content", str(human))
    assert trip_id in user_content, user_content
    assert "DRV-VERIFY" in user_content, user_content
    assert "1" in user_content, user_content
    print("OK: scoring agent received cache-backed data and invoked the graph.")


if __name__ == "__main__":
    asyncio.run(main())
