"""
Unified agent bases for TraceData.

- ``Agent``: LangGraph ReAct, one-shot ``invoke`` (e.g. orchestrator LLM routing).
- ``TDAgentBase``: Celery + ``IntentCapsule`` — cache, repos, lock release (domain agents).
- ``TDQueueAgentBase`` / ``TDLLMAgentBase``: legacy Redis queue consumer loop + optional ReAct.
- LLM adapter types: ``LLMAdapter``, ``LLMConfig``, model enums.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncEngine

from common.db.write_validation import DatabaseWriteValidator
from common.models.security import IntentCapsule
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

from .logger import get_agent_logger

logger = logging.getLogger(__name__)


# ── LangGraph (shared factory) ────────────────────────────────────────────────


def build_react_graph(llm: Any, tools: list, system_prompt: str) -> Any:
    """Create a LangGraph ReAct agent graph (single place for create_react_agent)."""
    from langgraph.prebuilt import create_react_agent

    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
    )


class Agent(ABC):
    """LangGraph ReAct helper: tools + LLM + ``invoke`` (orchestrator router pattern)."""

    def __init__(
        self,
        llm: Any,
        agent_name: str,
        tools: list,
        system_prompt: str,
    ):
        self.llm = llm
        self.agent_name = agent_name
        self.tools = tools
        self.system_prompt = system_prompt
        self._graph = None
        self.logger = get_agent_logger(agent_name)
        self.logger.info(
            "initialized agent | tools=%s | llm=%s",
            [t.name for t in self.tools],
            type(self.llm).__name__,
        )

    def _ensure_graph(self) -> Any:
        if self._graph is None:
            self.logger.info("creating langgraph agent")
            self._graph = build_react_graph(
                self.llm, self.tools, self.system_prompt
            )
        return self._graph

    def invoke(self, input_data: dict) -> dict:
        self.logger.info("invoke start | keys=%s", list(input_data.keys()))
        result = self._ensure_graph().invoke(input_data)
        self.logger.info("invoke complete")
        return result

    def __repr__(self) -> str:
        return f"{self.agent_name}(tools={len(self.tools)})"

    def __str__(self) -> str:
        tools_str = ", ".join([t.name for t in self.tools])
        return f"{self.agent_name}\n  Tools: {tools_str}\n  LLM: {self.llm}"


# ── LLM adapter contracts ───────────────────────────────────────────────────


class LLMAdapter(ABC):
    """Abstract adapter for provider-specific LangChain chat models."""

    @abstractmethod
    def get_chat_model(self) -> Any:
        raise NotImplementedError

    def __repr__(self) -> str:
        return self.__class__.__name__


class OpenAIModel(StrEnum):
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_35_TURBO = "gpt-3.5-turbo"


class AnthropicModel(StrEnum):
    CLAUDE_SONNET_4_20250514 = "claude-sonnet-4-20250514"
    CLAUDE_35_SONNET_20241022 = "claude-3-5-sonnet-20241022"
    CLAUDE_35_HAIKU_20241022 = "claude-3-5-haiku-20241022"
    CLAUDE_3_HAIKU_20240307 = "claude-3-haiku-20240307"


class LLMConfig(BaseModel):
    """Resolved LLM configuration returned by a factory."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    provider: str
    model: str
    adapter: LLMAdapter


def _extract_event_meta(event_data: dict[str, Any]) -> dict[str, Any]:
    if "trip_id" in event_data and "event" not in event_data:
        event_obj: dict[str, Any] = event_data
    else:
        event_obj = event_data.get("event", event_data) or {}

    return {
        "event_id": event_obj.get("event_id", "unknown"),
        "device_event_id": event_obj.get("device_event_id", "unknown"),
        "trip_id": event_obj.get("trip_id", "unknown"),
        "event_type": event_obj.get("event_type", "unknown"),
    }


# ── Redis queue worker (legacy) ──────────────────────────────────────────────


class TDQueueAgentBase(ABC):
    """
    Redis input queue consumer: pop → ``process_event`` → push to output queue.

    Prefer ``TDAgentBase`` for Celery + ``IntentCapsule`` workers.
    """

    def __init__(self, agent_name: str, input_queue: str, output_queue: str):
        self.agent_name = agent_name
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.redis = RedisClient()
        self._running = False

    @abstractmethod
    async def process_event(
        self, event_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        pass

    async def run(self) -> None:
        self._running = True
        logger.info(
            "[trace] agent_started agent=%s input_queue=%s output_queue=%s",
            self.agent_name,
            self.input_queue,
            self.output_queue,
        )

        try:
            while self._running:
                raw_event = await self.redis.pop(self.input_queue, timeout=5)
                if not raw_event:
                    continue

                try:
                    event_data = json.loads(raw_event)
                    meta = _extract_event_meta(event_data)
                    logger.info(
                        "[trace] redis_pop agent=%s queue=%s event_id=%s "
                        "device_event_id=%s trip_id=%s event_type=%s",
                        self.agent_name,
                        self.input_queue,
                        meta["event_id"],
                        meta["device_event_id"],
                        meta["trip_id"],
                        meta["event_type"],
                    )

                    result = await self.process_event(event_data)
                    logger.info(
                        "[trace] process_complete agent=%s event_id=%s status=%s",
                        self.agent_name,
                        meta["event_id"],
                        "result" if result else "no_result",
                    )

                    if result:
                        result["source_agent"] = self.agent_name
                        if "event_id" not in result:
                            result["event_id"] = meta["event_id"]

                        await self.redis.push(
                            self.output_queue, json.dumps(result)
                        )
                        logger.info(
                            "[trace] redis_push agent=%s queue=%s event_id=%s next_hop=%s",
                            self.agent_name,
                            self.output_queue,
                            result.get("event_id", "unknown"),
                            result.get("next_hop", "n/a"),
                        )

                except json.JSONDecodeError:
                    logger.error(
                        "[%s] Failed to decode event: %s",
                        self.agent_name,
                        raw_event,
                    )
                except Exception as e:
                    logger.exception(
                        "[%s] Error processing event: %s",
                        self.agent_name,
                        str(e),
                    )

        finally:
            await self.redis.close()
            logger.info("[trace] agent_stopped agent=%s", self.agent_name)

    def stop(self) -> None:
        self._running = False


class TDLLMAgentBase(TDQueueAgentBase):
    """Queue worker with LangGraph ReAct; call ``_invoke_llm`` from ``process_event``."""

    def __init__(
        self,
        agent_name: str,
        input_queue: str,
        output_queue: str,
        llm: Any,
        tools: list,
        system_prompt: str,
    ):
        super().__init__(agent_name, input_queue, output_queue)
        self.llm = llm
        self.tools = tools
        self.system_prompt = system_prompt
        self._react_agent = None
        logger.info(
            "[trace] llm_agent_initialized agent=%s tools=%s llm=%s",
            agent_name,
            [t.name for t in tools],
            type(llm).__name__,
        )

    def _get_react_agent(self) -> Any:
        if self._react_agent is None:
            logger.info("[trace] creating_react_agent agent=%s", self.agent_name)
            self._react_agent = build_react_graph(
                self.llm, self.tools, self.system_prompt
            )
        return self._react_agent

    def _invoke_llm(self, input_data: dict) -> dict:
        logger.info(
            "[trace] llm_invoke_start agent=%s keys=%s",
            self.agent_name,
            list(input_data.keys()),
        )
        result = self._get_react_agent().invoke(input_data)
        logger.info("[trace] llm_invoke_complete agent=%s", self.agent_name)
        return result


# ── Celery + IntentCapsule worker ────────────────────────────────────────────


class TDAgentBase(ABC):
    """
    Domain agents: ``IntentCapsule`` from Celery, scoped cache read, repo writes,
    lock release, completion publish.
    """

    AGENT_NAME: str

    def __init__(
        self,
        engine: AsyncEngine,
        redis_client: RedisClient | None = None,
    ):
        self._engine = engine
        self._redis = redis_client or RedisClient()
        self._write_validator = DatabaseWriteValidator.create_from_agent(
            self.AGENT_NAME or self.__class__.__name__.lower()
        )

    async def run(self, capsule_data: dict) -> dict[str, Any]:
        try:
            capsule = IntentCapsule.model_validate(capsule_data)
            trip_id = capsule.trip_id
            agent_name = capsule.agent

            logger.info(
                {
                    "action": "agent_run_start",
                    "agent": agent_name,
                    "trip_id": trip_id,
                }
            )

            cache_data = await self._read_cache(trip_id, capsule)
            result = await self._execute(trip_id, cache_data)

            output_key = RedisSchema.Trip.output(trip_id, agent_name)
            await self._redis._client.set(output_key, json.dumps(result))

            logger.info(
                {
                    "action": "agent_result_stored",
                    "agent": agent_name,
                    "trip_id": trip_id,
                    "output_key": output_key,
                }
            )

            await self._release_lock(trip_id, capsule.device_event_id)
            await self._publish_completion_event(
                trip_id, agent_name, "success", result
            )

            logger.info(
                {
                    "action": "agent_run_complete",
                    "agent": agent_name,
                    "trip_id": trip_id,
                    "status": "success",
                }
            )

            return result

        except Exception as e:
            logger.error(
                {
                    "action": "agent_run_error",
                    "agent": self.AGENT_NAME,
                    "trip_id": capsule.trip_id
                    if "capsule" in locals()
                    else "unknown",
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            )

            if "capsule" in locals():
                await self._publish_completion_event(
                    capsule.trip_id,
                    capsule.agent,
                    "failure",
                    {"error": str(e)},
                )

            raise

    @abstractmethod
    async def _execute(
        self,
        trip_id: str,
        cache_data: dict[str, Any],
    ) -> dict[str, Any]:
        raise NotImplementedError

    async def _read_cache(
        self,
        trip_id: str,
        capsule: IntentCapsule,
    ) -> dict[str, Any]:
        cache_data: dict[str, Any] = {}
        read_keys = (
            list(capsule.token.read_keys) if capsule.token else []
        )

        for key in read_keys:
            try:
                value = await self._redis._client.get(key)
                if value:
                    cache_data[key] = json.loads(value)
                else:
                    logger.warning(
                        {
                            "action": "cache_key_not_found",
                            "trip_id": trip_id,
                            "key": key,
                        }
                    )
            except Exception as e:
                logger.error(
                    {
                        "action": "cache_read_error",
                        "trip_id": trip_id,
                        "key": key,
                        "error": str(e),
                    }
                )

        logger.info(
            {
                "action": "cache_read_complete",
                "trip_id": trip_id,
                "agent": capsule.agent,
                "keys_loaded": len(cache_data),
                "keys_requested": len(read_keys),
            }
        )

        return cache_data

    async def _release_lock(
        self,
        trip_id: str,
        device_event_id: str | None = None,
    ) -> None:
        try:
            from agents.orchestrator.db_manager import DBManager

            db_manager = DBManager()
            resolved_id = (device_event_id or "").strip()

            if not resolved_id:
                from common.db.repositories.events_repo import EventsRepo

                events_repo = EventsRepo(self._engine)
                recent_event = await events_repo.get_latest_event_for_trip(
                    trip_id
                )
                if recent_event:
                    resolved_id = (
                        recent_event.get("device_event_id") or ""
                    ).strip()

            if resolved_id:
                await db_manager.release_lock(resolved_id)
                logger.info(
                    {
                        "action": "lock_released",
                        "trip_id": trip_id,
                        "device_event_id": resolved_id,
                    }
                )
            else:
                logger.warning(
                    {
                        "action": "no_event_found_for_lock_release",
                        "trip_id": trip_id,
                    }
                )

        except Exception as e:
            logger.error(
                {
                    "action": "lock_release_error",
                    "trip_id": trip_id,
                    "error": str(e),
                }
            )

    async def _publish_completion_event(
        self,
        trip_id: str,
        agent_name: str,
        status: str,
        result: dict,
    ) -> None:
        try:
            completion_event = {
                "trip_id": trip_id,
                "agent": agent_name,
                "status": status,
                "completed_at": datetime.now(UTC).isoformat(),
                "result": result,
            }

            channel = RedisSchema.Trip.events_channel(trip_id)
            await self._redis._client.publish(
                channel,
                json.dumps(completion_event),
            )

            logger.info(
                {
                    "action": "completion_event_published",
                    "trip_id": trip_id,
                    "agent": agent_name,
                    "status": status,
                    "channel": channel,
                }
            )

        except Exception as e:
            logger.error(
                {
                    "action": "completion_event_publish_error",
                    "trip_id": trip_id,
                    "agent": agent_name,
                    "error": str(e),
                }
            )

    async def _validate_write(self, table_name: str) -> bool:
        return self._write_validator.validate_write(table_name)

    @abstractmethod
    def _get_repos(self) -> dict[str, Any]:
        raise NotImplementedError
