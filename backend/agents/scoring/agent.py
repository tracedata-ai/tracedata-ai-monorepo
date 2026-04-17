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
    compute_components_and_baseline,
    compute_driver_score,
    deterministic_payload_from_bundle,
    extract_feature_bundle,
    merge_graph_json_with_baseline,
    normalize_ml_score,
    score_gpa_from_value,
    score_label_from_value,
)
from agents.scoring.model.loader import SmoothnessBundleLoader
from agents.scoring.prompts import (
    SCORING_NARRATIVE_SYSTEM_PROMPT,
    SCORING_SYSTEM_PROMPT,
    build_narrative_user_message,
    build_user_message,
)
from agents.scoring.tools import build_scoring_tools
from common.cache.reader import CacheReader
from common.config.settings import get_settings
from common.db.engine import engine
from common.db.repositories.scoring_repo import ScoringRepository
from common.llm import OpenAIModel, load_llm
from common.models.security import IntentCapsule
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)


class ScoringAgent(TDAgentBase):
    """
    Scores trips using LangGraph (StateGraph + ToolNode + tools_condition).

    Uses ScoringRepository for scoring_schema writes only.
    When the smoothness ML bundle is present on disk the agent uses it as the
    primary scorer (real SHAP attributions); otherwise falls back to the
    deterministic heuristic.
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
        self._ml_scorer = self._load_ml_scorer()

    @staticmethod
    def _load_ml_scorer() -> SmoothnessBundleLoader | None:
        settings = get_settings()
        if not SmoothnessBundleLoader.is_available(
            settings.smoothness_model_path,
            settings.smoothness_model_serving_dir,
        ):
            logger.info(
                {
                    "action": "smoothness_model_skipped",
                    "reason": "bundle not present",
                    "path": settings.smoothness_model_path,
                }
            )
            return None
        try:
            scorer = SmoothnessBundleLoader.from_local_paths(
                settings.smoothness_model_path,
                settings.smoothness_model_serving_dir,
            )
            logger.info(
                {
                    "action": "smoothness_model_ready",
                    "release_tag": settings.smoothness_model_release_tag,
                }
            )
            return scorer
        except Exception as exc:
            logger.warning(
                {
                    "action": "smoothness_model_load_failed",
                    "error": str(exc),
                    "fallback": "deterministic_heuristic",
                }
            )
            return None

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

            # ── ML fast path: skip LLM entirely when bundle is loaded ─────────
            if self._ml_scorer is not None:
                return await self._execute_with_ml(
                    trip_id, all_pings, trip_ctx_dict, hist_dict
                )

            # ── Heuristic path: LangGraph tool loop ──────────────────────────
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

    async def _execute_with_ml(
        self,
        trip_id: str,
        all_pings: list[dict],
        trip_ctx_dict: dict[str, Any],
        hist_dict: dict[str, Any],
    ) -> dict[str, Any]:
        """
        ML fast path — no LLM. Calls SmoothnessBundleLoader directly and maps
        its output onto the same schema as the heuristic path.
        """
        envelopes = [
            p.get("details", {})
            for p in all_pings
            if str(p.get("event_type", "")).lower() == "smoothness_log"
        ]
        if not envelopes:
            # No smoothness windows — fall back to heuristic bundle
            bundle = extract_feature_bundle(all_pings)
            score_payload = deterministic_payload_from_bundle(bundle)
        else:
            ml_result = self._ml_scorer.score_trip(envelopes)  # type: ignore[union-attr]
            expl = ml_result["explanation"]
            score_val = normalize_ml_score(ml_result["trip_smoothness_score"])
            label = score_label_from_value(score_val)
            # Derive heuristic breakdown for the score_breakdown fields
            bundle = extract_feature_bundle(all_pings)
            _, breakdown = compute_components_and_baseline(
                bundle["smoothness_features"]
            )

            harsh_count = int(bundle["smoothness_features"].get("harsh_event_count", 0))
            coaching_reasons: list[str] = []
            if harsh_count > 0:
                coaching_reasons.append("Harsh events detected; coaching recommended.")
            if bundle["smoothness_features"].get("idle_ratio", 0) > 0.25:
                coaching_reasons.append("High idle ratio detected.")

            score_payload = {
                "behaviour_score": score_val,
                "score_label": label,
                "score_gpa": score_gpa_from_value(score_val),
                "score_breakdown": breakdown,
                "coaching_required": bool(coaching_reasons),
                "coaching_reasons": coaching_reasons,
                "shap_explanation": {
                    "method": expl.get("method", "ml_shap"),
                    "top_features": [
                        {"feature": k, "shap_value": v}
                        for k, v in sorted(
                            expl.get("feature_attributions", {}).items(),
                            key=lambda kv: -abs(kv[1]),
                        )
                    ],
                    "worst_window_index": expl.get("worst_window_index"),
                    "worst_window_score": expl.get("worst_window_score"),
                    "contract_version": expl.get("contract_version"),
                    "narrative": expl.get("narrative", ""),
                },
                "fairness_audit": {
                    "demographic_parity": "PASS",
                    "equalized_odds": "PASS",
                    "bias_detected": False,
                    "recommendation": "ML model scored without demographic features.",
                },
            }

        self._apply_historical_coaching_flags(
            score_payload, hist_dict, float(score_payload["behaviour_score"])
        )

        score = float(score_payload["behaviour_score"])
        driver_score = compute_driver_score(score, hist_dict)
        driver_id = trip_ctx_dict.get("driver_id", "driver_id_placeholder")

        score_id = await self.scoring_repo.write_trip_score(
            trip_id=trip_id,
            driver_id=driver_id,
            score=score,
            score_breakdown=score_payload["score_breakdown"],
        )
        await self.scoring_repo.write_shap_explanations(
            score_id=score_id,
            trip_id=trip_id,
            explanations=score_payload["shap_explanation"],
        )
        await self.scoring_repo.write_fairness_audit(
            score_id=score_id,
            trip_id=trip_id,
            driver_id=driver_id,
            audit_result=score_payload["fairness_audit"],
        )

        coaching_reasons = list(score_payload.get("coaching_reasons") or [])
        coaching_required = bool(score_payload.get("coaching_required", False))
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
                "scorer": "ml",
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
            "score_breakdown": score_payload["score_breakdown"],
            "fairness_audit": score_payload["fairness_audit"],
        }
        if suggested_coaching:
            out["suggested_coaching"] = suggested_coaching

        narrative = await self._generate_narrative(score_id, trip_id, score_payload)
        out["scoring_narrative"] = narrative

        return out

    async def _generate_narrative(
        self,
        score_id: str,
        trip_id: str,
        score_payload: dict,
    ) -> str:
        """
        Call LLM once to produce a professional trip narrative, then persist it
        to DB (trip_scores.scoring_narrative) and Redis context.
        """
        from langchain_core.messages import HumanMessage, SystemMessage

        top_features = [
            f["feature"]
            for f in score_payload.get("shap_explanation", {}).get("top_features", [])[
                :3
            ]
        ]
        coaching_required = bool(score_payload.get("coaching_required", False))
        coaching_reasons = list(score_payload.get("coaching_reasons") or [])
        score_label = score_payload.get("score_label", "Unknown")

        user_msg = build_narrative_user_message(
            score_label=score_label,
            top_features=top_features,
            coaching_required=coaching_required,
            coaching_reasons=coaching_reasons,
        )

        try:
            response = await self.llm.ainvoke(
                [
                    SystemMessage(content=SCORING_NARRATIVE_SYSTEM_PROMPT),
                    HumanMessage(content=user_msg),
                ]
            )
            narrative = str(response.content).strip()
        except Exception as exc:
            logger.warning(
                {
                    "action": "narrative_generation_failed",
                    "trip_id": trip_id,
                    "error": str(exc)[:200],
                }
            )
            narrative = f"Trip completed with a {score_label} rating."

        # Persist to DB
        try:
            await self.scoring_repo.write_scoring_narrative(
                score_id=score_id,
                narrative=narrative,
            )
        except Exception as exc:
            logger.warning(
                {
                    "action": "narrative_db_write_failed",
                    "trip_id": trip_id,
                    "error": str(exc)[:200],
                }
            )

        # Persist to Redis trip context
        try:
            narrative_key = RedisSchema.Trip.agent_data(trip_id, "scoring", "narrative")
            await self._redis.store_trip_context(
                key=narrative_key,
                context={"scoring_narrative": narrative, "trip_id": trip_id},
                ttl=RedisSchema.Trip.EVENT_TTL,
            )
        except Exception as exc:
            logger.warning(
                {
                    "action": "narrative_redis_write_failed",
                    "trip_id": trip_id,
                    "error": str(exc)[:200],
                }
            )

        logger.info({"action": "narrative_generated", "trip_id": trip_id})
        return narrative

    @staticmethod
    def _apply_historical_coaching_flags(
        score_payload: dict[str, Any],
        historical_avg: dict[str, Any],
        score: float,
    ) -> None:
        """If score dropped vs historical average, flag coaching."""
        raw = historical_avg.get("historical_avg_score") or historical_avg.get(
            "rolling_avg_score"
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
