"""
Support Agent — TDAgentBase + LangGraph tool loop (+ deterministic fallback).

Uses SupportRepository for coaching_schema writes only.
"""

import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from agents.base.agent import TDAgentBase
from agents.base.langgraph_runner import (
    build_tool_loop_graph,
    parse_json_from_last_ai_message,
)
from agents.driver_support.prompts import (
    SUPPORT_SYSTEM_PROMPT,
    build_support_user_message,
)
from agents.driver_support.tools import (
    baseline_support_coaching,
    build_support_tools,
    merge_support_json_with_baseline,
)
from common.cache.reader import CacheReader
from common.db.engine import engine
from common.db.repositories.support_repo import SupportRepository
from common.llm import OpenAIModel, load_llm
from common.models.security import IntentCapsule
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)


class SupportAgent(TDAgentBase):
    """Post-trip and event-driven coaching via LangGraph tools + SupportRepository."""

    AGENT_NAME = "support"

    def __init__(
        self,
        engine_param=None,
        redis_client: RedisClient | None = None,
        llm: Any | None = None,
    ):
        super().__init__(engine_param or engine, redis_client)
        self.support_repo = SupportRepository(self._engine)
        if llm is not None:
            self._llm = llm
        else:
            try:
                self._llm = load_llm(OpenAIModel.GPT_4O_MINI).adapter.get_chat_model()
            except Exception as exc:
                logger.warning(
                    {"action": "support_llm_unavailable", "error": str(exc)},
                )
                self._llm = None

    async def run(self, capsule_data: dict) -> dict[str, Any]:
        capsule = IntentCapsule.model_validate(capsule_data)
        result = await super().run(capsule_data)
        if result.get("status") != "success":
            return result

        await self._update_trip_context_with_support_output(capsule.trip_id, result)
        return result

    async def _execute(
        self,
        trip_id: str,
        cache_data: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            raw = CacheReader.by_key_markers(
                cache_data,
                "trip_context",
                "coaching_history",
                "current_event",
            )
            trip_context = (
                raw["trip_context"] if isinstance(raw["trip_context"], dict) else None
            )
            coaching_history = (
                raw["coaching_history"]
                if isinstance(raw["coaching_history"], list)
                else []
            )
            current_event = (
                raw["current_event"] if isinstance(raw["current_event"], dict) else None
            )
            scoring_snapshot = (
                (trip_context or {}).get("scoring_output") if trip_context else None
            )
            safety_snapshot = (
                (trip_context or {}).get("safety_output") if trip_context else None
            )

            driver_id = (
                (trip_context or {}).get("driver_id", "driver_id_placeholder")
                if trip_context
                else "driver_id_placeholder"
            )

            baseline = baseline_support_coaching(
                trip_context,
                coaching_history,
                current_event,
                scoring_snapshot,
                safety_snapshot,
            )
            merged = baseline

            if self._llm is not None:
                tools = build_support_tools(
                    trip_context,
                    coaching_history,
                    current_event,
                    scoring_snapshot,
                    safety_snapshot,
                )
                graph = build_tool_loop_graph(self._llm, tools)
                driver_hint = str(driver_id)
                messages = [
                    SystemMessage(content=SUPPORT_SYSTEM_PROMPT),
                    HumanMessage(
                        content=build_support_user_message(trip_id, driver_hint)
                    ),
                ]
                thread_id = f"{trip_id}:support:run"
                config = {"configurable": {"thread_id": thread_id}}
                result = await graph.ainvoke({"messages": messages}, config=config)
                parsed = parse_json_from_last_ai_message(result)
                merged = merge_support_json_with_baseline(parsed, baseline)

            coaching_category = merged["coaching_category"]
            coaching_message = merged["message"]
            priority = merged["priority"]

            coaching_id = await self.support_repo.write_coaching(
                trip_id=trip_id,
                driver_id=driver_id,
                coaching_category=coaching_category,
                message=coaching_message,
                priority=priority,
            )

            logger.info(
                {
                    "action": "coaching_generated",
                    "trip_id": trip_id,
                    "coaching_id": coaching_id,
                }
            )

            return {
                "status": "success",
                "coaching_id": coaching_id,
                "message": coaching_message,
                "coaching_category": coaching_category,
                "priority": priority,
                "trip_id": trip_id,
            }

        except Exception as e:
            logger.error(
                {
                    "action": "coaching_generation_error",
                    "trip_id": trip_id,
                    "error": str(e),
                }
            )
            raise

    def _get_repos(self) -> dict[str, Any]:
        return {"support_repo": self.support_repo}

    async def _update_trip_context_with_support_output(
        self, trip_id: str, support_output: dict[str, Any]
    ) -> None:
        """Persist latest support output summary into trip runtime context."""
        context_key = RedisSchema.Trip.context(trip_id)
        existing = await self._redis.get_trip_context(context_key)
        context = existing if isinstance(existing, dict) else {}
        context["latest_support_output"] = {
            "status": support_output.get("status"),
            "coaching_id": support_output.get("coaching_id"),
            "message": support_output.get("message"),
            "trip_id": support_output.get("trip_id", trip_id),
        }
        context.setdefault("trip_id", trip_id)
        await self._redis.store_trip_context(
            context_key,
            context,
            ttl=RedisSchema.Trip.CONTEXT_TTL_HIGH,
        )
