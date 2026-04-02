"""
Scoring Agent — TDAgentBase lifecycle + explicit LangGraph tool loop.

Reasoning and tool use happen only inside the compiled graph (chatbot + ToolNode).
"""

import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from agents.base.agent import TDAgentBase
from agents.base.langgraph_runner import (
    build_tool_loop_graph,
    parse_json_from_last_ai_message,
)
from agents.scoring.features import (
    compute_driver_score,
    deterministic_payload_from_bundle,
    extract_feature_bundle,
    merge_graph_json_with_baseline,
)
from agents.scoring.prompts import SCORING_SYSTEM_PROMPT, build_user_message
from agents.scoring.tools import build_scoring_tools
from common.cache.reader import CacheReader
from common.db.engine import engine
from common.db.repositories.scoring_repo import ScoringRepository
from common.models.security import IntentCapsule
from common.llm import OpenAIModel, load_llm
from common.redis.client import RedisClient

logger = logging.getLogger(__name__)


class ScoringAgent(TDAgentBase):
    """
    Scores trips using LangGraph (StateGraph + ToolNode + tools_condition).

    Uses ScoringRepository for scoring_schema writes only.
    """

    AGENT_NAME = "scoring"

    def __init__(
        self,
        engine_param=None,
        redis_client: RedisClient | None = None,
        llm: Any | None = None,
    ):
        super().__init__(engine_param or engine, redis_client)
        self.scoring_repo = ScoringRepository(self._engine)
        self.llm = llm or load_llm(OpenAIModel.GPT_4O_MINI).adapter.get_chat_model()

    async def run(self, capsule_data: dict) -> dict[str, Any]:
        capsule = IntentCapsule.model_validate(capsule_data)
        result = await super().run(capsule_data)
        if result.get("status") != "success":
            return result
        from agents.orchestrator.coaching_followup import (
            schedule_coaching_ready_if_pending,
        )

        await schedule_coaching_ready_if_pending(
            redis=self._redis,
            engine=self._engine,
            trip_id=capsule.trip_id,
        )
        return result

    async def _execute(
        self,
        trip_id: str,
        cache_data: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            found = CacheReader.by_key_markers(
                cache_data, "all_pings", "historical_avg", "trip_context"
            )
            all_pings = found["all_pings"]
            historical_avg = found["historical_avg"]
            trip_context = found["trip_context"]

            if not all_pings:
                return {
                    "status": "error",
                    "reason": "no_pings_data",
                    "trip_id": trip_id,
                }

            trip_ctx_dict = trip_context if isinstance(trip_context, dict) else {}
            hist_dict = historical_avg if isinstance(historical_avg, dict) else {}

            tools = build_scoring_tools(all_pings, trip_ctx_dict, hist_dict)
            graph = build_tool_loop_graph(self.llm, tools)

            driver_hint = str(trip_ctx_dict.get("driver_id", "unknown"))
            user_content = build_user_message(trip_id, len(all_pings), driver_hint)
            messages = [
                SystemMessage(content=SCORING_SYSTEM_PROMPT),
                HumanMessage(content=user_content),
            ]

            thread_id = f"{trip_id}:scoring:run"
            config = {"configurable": {"thread_id": thread_id}}

            result = await graph.ainvoke({"messages": messages}, config=config)

            bundle = extract_feature_bundle(all_pings)
            parsed = parse_json_from_last_ai_message(result)
            if parsed is None:
                score_payload = deterministic_payload_from_bundle(bundle)
            else:
                score_payload = merge_graph_json_with_baseline(parsed, bundle)

            self._apply_historical_coaching_flags(
                score_payload, hist_dict, float(score_payload["behaviour_score"])
            )

            score = float(score_payload["behaviour_score"])
            driver_score = compute_driver_score(score, hist_dict)
            explanations = score_payload["shap_explanation"]
            fairness_audit = score_payload["fairness_audit"]
            score_breakdown = score_payload["score_breakdown"]
            coaching_reasons = list(score_payload.get("coaching_reasons") or [])
            coaching_required = bool(score_payload.get("coaching_required", False))

            score_id = await self.scoring_repo.write_trip_score(
                trip_id=trip_id,
                driver_id=trip_ctx_dict.get("driver_id", "driver_id_placeholder"),
                score=score,
                score_breakdown=score_breakdown,
            )

            await self.scoring_repo.write_shap_explanations(
                score_id=score_id,
                trip_id=trip_id,
                explanations=explanations,
            )

            await self.scoring_repo.write_fairness_audit(
                score_id=score_id,
                trip_id=trip_id,
                driver_id=trip_ctx_dict.get("driver_id", "driver_id_placeholder"),
                audit_result=fairness_audit,
            )

            suggested_coaching = None
            if coaching_required or score < 60:
                suggested_coaching = {
                    "category": "smoothness_improvement",
                    "message": "Trip score indicates need for coaching on smoothness.",
                    "priority": "high",
                    "reasons": coaching_reasons,
                }

            logger.info(
                {
                    "action": "scoring_complete",
                    "trip_id": trip_id,
                    "trip_score": score,
                    "driver_score": driver_score,
                    "score_id": score_id,
                }
            )

            out: dict[str, Any] = {
                "status": "success",
                "score": score,
                "trip_score": score,
                "driver_score": driver_score,
                "score_id": score_id,
                "trip_id": trip_id,
                "ping_count": len(all_pings),
                "score_label": score_payload["score_label"],
                "score_breakdown": score_breakdown,
                "fairness_audit": fairness_audit,
            }
            if suggested_coaching:
                out["suggested_coaching"] = suggested_coaching
            return out

        except Exception as e:
            logger.error(
                {
                    "action": "scoring_error",
                    "trip_id": trip_id,
                    "error": str(e),
                }
            )
            raise

    @staticmethod
    def _apply_historical_coaching_flags(
        score_payload: dict[str, Any],
        historical_avg: dict[str, Any],
        score: float,
    ) -> None:
        """If score dropped vs historical average, flag coaching."""
        raw = (
            historical_avg.get("historical_avg_score")
            or historical_avg.get("rolling_avg_score")
        )
        if raw is None:
            return
        try:
            baseline = float(raw)
        except (TypeError, ValueError):
            return
        if score < baseline - 10.0:
            reasons = list(score_payload.get("coaching_reasons") or [])
            reasons.append(
                f"Score dropped more than 10 points vs historical average ({baseline:.1f})."
            )
            score_payload["coaching_reasons"] = reasons
            score_payload["coaching_required"] = True

    def _get_repos(self) -> dict[str, Any]:
        return {"scoring_repo": self.scoring_repo}
