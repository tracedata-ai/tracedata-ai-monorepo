"""
Safety Agent — TDAgentBase + LangGraph tool loop (+ deterministic fallback).

Uses SafetyRepository for safety_schema writes only.
"""

import logging
from datetime import datetime
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from agents.base.agent import TDAgentBase
from agents.base.langgraph_runner import (
    build_tool_loop_graph,
    parse_json_from_last_ai_message,
)
from agents.safety.prompts import SAFETY_SYSTEM_PROMPT, build_safety_user_message
from agents.safety.tools import (
    baseline_safety_assessment,
    build_safety_tools,
    merge_safety_json_with_baseline,
)
from common.cache.reader import CacheReader
from common.db.engine import engine as default_db_engine
from common.db.repositories.safety_repo import SafetyRepository
from common.llm import OpenAIModel, load_llm
from common.models.security import IntentCapsule
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)


class SafetyAgent(TDAgentBase):
    """
    Safety-critical event triage via LangGraph (tools + optional LLM), then repo writes.
    """

    AGENT_NAME = "safety"

    def __init__(
        self,
        engine_param=None,
        redis_client: RedisClient | None = None,
        llm: Any | None = None,
    ):
        super().__init__(engine_param or default_db_engine, redis_client)
        self.safety_repo = SafetyRepository(self._engine)
        if llm is not None:
            self._llm = llm
        else:
            try:
                self._llm = load_llm(OpenAIModel.GPT_4O_MINI).adapter.get_chat_model()
            except Exception as exc:
                logger.warning(
                    {"action": "safety_llm_unavailable", "error": str(exc)},
                )
                self._llm = None

    async def run(self, capsule_data: dict) -> dict[str, Any]:
        capsule = IntentCapsule.model_validate(capsule_data)
        result = await super().run(capsule_data)
        if result.get("status") != "success":
            return result
        await self._update_trip_context_with_safety_output(capsule.trip_id, result)
        return result

    async def _update_trip_context_with_safety_output(
        self, trip_id: str, safety_output: dict[str, Any]
    ) -> None:
        """Merge latest safety summary into trip runtime context (Redis)."""
        context_key = RedisSchema.Trip.context(trip_id)
        existing = await self._redis.get_trip_context(context_key)
        context = existing if isinstance(existing, dict) else {}
        context["latest_safety_output"] = {
            "status": safety_output.get("status"),
            "decision_id": safety_output.get("decision_id"),
            "decision": safety_output.get("decision"),
            "action": safety_output.get("action"),
            "severity": safety_output.get("severity"),
            "trip_id": safety_output.get("trip_id", trip_id),
        }
        context.setdefault("trip_id", trip_id)
        await self._redis.store_trip_context(
            context_key,
            context,
            ttl=RedisSchema.Trip.CONTEXT_TTL_HIGH,
        )

    async def _execute(
        self,
        trip_id: str,
        cache_data: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            found = CacheReader.by_key_markers(
                cache_data, "current_event", "trip_context"
            )
            current_event = found["current_event"]
            trip_context = found["trip_context"]
            trip_ctx_dict = trip_context if isinstance(trip_context, dict) else {}

            if not current_event or not isinstance(current_event, dict):
                return {
                    "status": "error",
                    "reason": "no_event_data",
                    "trip_id": trip_id,
                }

            baseline = baseline_safety_assessment(current_event, trip_ctx_dict)
            merged = baseline

            # Early place_name extraction for LLM context
            _loc_early = current_event.get("location")
            place_name = (
                (_loc_early.get("place_name") or "").strip() or None
                if isinstance(_loc_early, dict)
                else None
            )

            if self._llm is not None:
                tools = build_safety_tools(current_event, trip_ctx_dict)
                graph = build_tool_loop_graph(self._llm, tools)
                evt_type = str(current_event.get("event_type", "unknown"))
                messages = [
                    SystemMessage(content=SAFETY_SYSTEM_PROMPT),
                    HumanMessage(
                        content=build_safety_user_message(trip_id, evt_type, place_name)
                    ),
                ]
                thread_id = (
                    f"{trip_id}:safety:run:{current_event.get('event_id', 'evt')}"
                )
                config = {"configurable": {"thread_id": thread_id}}
                result = await graph.ainvoke({"messages": messages}, config=config)
                parsed = parse_json_from_last_ai_message(result)
                merged = merge_safety_json_with_baseline(parsed, baseline)

            severity = float(merged["severity"])
            action = str(merged["action"])
            decision = str(merged["decision"])
            reason = str(merged["reason"])

            # Capture structured incident fields for audit/reporting.
            location = current_event.get("location")
            lat = None
            lon = None
            if isinstance(location, dict):
                lat_raw = location.get("lat")
                lon_raw = location.get("lon")
                lat = None
                lon = None
                if lat_raw is not None:
                    try:
                        lat = float(lat_raw)
                    except (TypeError, ValueError):
                        lat = None
                if lon_raw is not None:
                    try:
                        lon = float(lon_raw)
                    except (TypeError, ValueError):
                        lon = None

            event_timestamp = None
            ts_raw = current_event.get("timestamp")
            if isinstance(ts_raw, str):
                try:
                    event_timestamp = datetime.fromisoformat(
                        ts_raw.replace("Z", "+00:00")
                    )
                except ValueError:
                    event_timestamp = None

            details = current_event.get("details")
            traffic_conditions = None
            weather_conditions = None
            if isinstance(details, dict):
                traffic_val = details.get("traffic_conditions")
                weather_val = details.get("weather_conditions")
                traffic_conditions = (
                    str(traffic_val).strip()
                    if isinstance(traffic_val, (str, int, float))
                    else None
                )
                weather_conditions = (
                    str(weather_val).strip()
                    if isinstance(weather_val, (str, int, float))
                    else None
                )

            decision_id = await self.safety_repo.write_safety_decision(
                event_id=current_event.get("event_id"),
                trip_id=trip_id,
                decision=decision,
                action=action,
                reason=reason,
                recommended_action=action,
            )

            await self.safety_repo.write_harsh_event_analysis(
                event_id=current_event.get("event_id"),
                trip_id=trip_id,
                event_type=current_event.get("event_type"),
                severity=current_event.get("severity", "unknown"),
                event_timestamp=event_timestamp,
                lat=lat,
                lon=lon,
                location_name=place_name,
                traffic_conditions=traffic_conditions,
                weather_conditions=weather_conditions,
                analysis={
                    "assessed_severity": severity,
                    "trip_context": trip_ctx_dict,
                    "recommended_action": action,
                    "llm_path": bool(self._llm),
                    "reason": reason,
                    "event_timestamp": ts_raw,
                    "location": {"lat": lat, "lon": lon, "place_name": place_name},
                    "traffic_conditions": traffic_conditions,
                    "weather_conditions": weather_conditions,
                },
            )

            logger.info(
                {
                    "action": "safety_analysis_complete",
                    "trip_id": trip_id,
                    "severity": severity,
                    "decision_id": decision_id,
                }
            )

            return {
                "status": "success",
                "severity": severity,
                "action": action,
                "decision": decision,
                "decision_id": decision_id,
                "trip_id": trip_id,
            }

        except Exception as e:
            logger.error(
                {
                    "action": "safety_analysis_error",
                    "trip_id": trip_id,
                    "error": str(e),
                }
            )
            raise

    def _get_repos(self) -> dict[str, Any]:
        return {"safety_repo": self.safety_repo}
