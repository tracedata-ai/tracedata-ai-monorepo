import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from common.config.settings import get_settings
from common.redis.client import RedisClient

logger = logging.getLogger(__name__)
settings = get_settings()


# ---------------------------------------------------------------------------
# LLM adapter contracts (adapted from references/reference/adapters)
# ---------------------------------------------------------------------------

from abc import abstractmethod as _abstractmethod
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class LLMAdapter(ABC):
    """Abstract adapter for provider-specific LangChain chat models."""

    @_abstractmethod
    def get_chat_model(self) -> Any:
        """Return a LangChain-compatible chat model instance."""
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
    """Resolved LLM configuration returned by the factory."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    provider: str
    model: str
    adapter: LLMAdapter


def _extract_event_meta(event_data: dict[str, Any]) -> dict[str, Any]:
    """Normalizes event fields for consistent trace logging.

    Handles both wrapped shape (TelemetryPacket with nested 'event' field)
    and flat shape (direct TripEvent dict).
    """
    # Flat TripEvent — top-level trip_id key indicates unwrapped shape
    if "trip_id" in event_data and "event" not in event_data:
        event_obj: dict[str, Any] = event_data
    else:
        # Wrapped TelemetryPacket or fallback
        event_obj = event_data.get("event", event_data) or {}

    return {
        "event_id": event_obj.get("event_id", "unknown"),
        "device_event_id": event_obj.get("device_event_id", "unknown"),
        "trip_id": event_obj.get("trip_id", "unknown"),
        "event_type": event_obj.get("event_type", "unknown"),
    }


class TDAgentBase(ABC):
    """
    Thick base class for all TraceData agents.

    Handles Redis connectivity, event consumption, and result publishing.
    Subclasses only need to implement `process_event`.
    """

    def __init__(self, agent_name: str, input_queue: str, output_queue: str):
        self.agent_name = agent_name
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.redis = RedisClient()
        self._running = False

    @abstractmethod
    async def process_event(self, event_data: dict[str, Any]) -> dict[str, Any] | None:
        """
        Business logic for the specific agent.
        Returns a dictionary to be published, or None to skip publishing.
        """
        pass

    async def run(self):
        """Infinite loop consuming events from the input queue."""
        self._running = True
        logger.info(
            "[trace] agent_started agent=%s input_queue=%s output_queue=%s",
            self.agent_name,
            self.input_queue,
            self.output_queue,
        )

        try:
            while self._running:
                # Blocking pop from Redis
                raw_event = await self.redis.pop(self.input_queue, timeout=5)
                if not raw_event:
                    continue

                try:
                    event_data = json.loads(raw_event)
                    meta = _extract_event_meta(event_data)
                    logger.info(
                        "[trace] redis_pop agent=%s queue=%s event_id=%s device_event_id=%s trip_id=%s event_type=%s",
                        self.agent_name,
                        self.input_queue,
                        meta["event_id"],
                        meta["device_event_id"],
                        meta["trip_id"],
                        meta["event_type"],
                    )

                    # Core processing logic
                    result = await self.process_event(event_data)
                    logger.info(
                        "[trace] process_complete agent=%s event_id=%s status=%s",
                        self.agent_name,
                        meta["event_id"],
                        "result" if result else "no_result",
                    )

                    if result:
                        # Add metadata
                        result["source_agent"] = self.agent_name
                        if "event_id" not in result:
                            result["event_id"] = meta["event_id"]

                        # Publish back to Redis
                        await self.redis.push(self.output_queue, json.dumps(result))
                        logger.info(
                            "[trace] redis_push agent=%s queue=%s event_id=%s next_hop=%s",
                            self.agent_name,
                            self.output_queue,
                            result.get("event_id", "unknown"),
                            result.get("next_hop", "n/a"),
                        )

                except json.JSONDecodeError:
                    logger.error(
                        f"[{self.agent_name}] Failed to decode event: {raw_event}"
                    )
                except Exception as e:
                    logger.exception(
                        f"[{self.agent_name}] Error processing event: {str(e)}"
                    )

        finally:
            await self.redis.close()
            logger.info("[trace] agent_stopped agent=%s", self.agent_name)

    def stop(self):
        self._running = False


# ---------------------------------------------------------------------------
# LLM-capable base (adapted from references/reference/agents/base.py)
# ---------------------------------------------------------------------------


class TDLLMAgentBase(TDAgentBase):
    """Extends TDAgentBase with a LangGraph ReAct agent.

    Subclasses pass a LangChain chat model, a list of tools, and a system
    prompt.  Call `self._invoke_llm(input_data)` from `process_event` to run
    the ReAct loop.
    """

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

    def _get_react_agent(self):
        if self._react_agent is None:
            from langgraph.prebuilt import create_react_agent

            logger.info("[trace] creating_react_agent agent=%s", self.agent_name)
            self._react_agent = create_react_agent(
                model=self.llm,
                tools=self.tools,
                prompt=self.system_prompt,
            )
        return self._react_agent

    def _invoke_llm(self, input_data: dict) -> dict:
        """Run the ReAct agent synchronously and return its result dict."""
        logger.info(
            "[trace] llm_invoke_start agent=%s keys=%s",
            self.agent_name,
            list(input_data.keys()),
        )
        result = self._get_react_agent().invoke(input_data)
        logger.info("[trace] llm_invoke_complete agent=%s", self.agent_name)
        return result
