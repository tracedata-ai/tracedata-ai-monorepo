import json
import logging
from abc import ABC, abstractmethod
from typing import Annotated, Any

from langchain_core.messages import AnyMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from common.config.settings import get_settings
from common.redis.client import RedisClient

logger = logging.getLogger(__name__)
settings = get_settings()


class _AgentState(TypedDict):
    """LangGraph state shared across all agent graph instances."""

    messages: Annotated[list[AnyMessage], add_messages]


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

    Handles Redis connectivity, event consumption, result publishing, and
    LangGraph-powered LLM reasoning.

    Subclasses configure agent behaviour by overriding class-level attributes:
      - SYSTEM_PROMPT: str   — system instruction for the LLM
      - tools: list          — LangChain tools the agent may call

    The LangGraph loop (chatbot → tools → chatbot) is built lazily on first
    use so that agents without an LLM key still work as plain event processors.
    """

    # ── Subclass configuration ─────────────────────────────────────────────────
    SYSTEM_PROMPT: str = ""
    tools: list = []

    def __init__(self, agent_name: str, input_queue: str, output_queue: str):
        self.agent_name = agent_name
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.redis = RedisClient()
        self._running = False
        self._graph: StateGraph | None = None

    # ── LangGraph wiring ───────────────────────────────────────────────────────

    def _get_checkpointer(self) -> BaseCheckpointSaver:
        """
        Return the checkpointer for conversation persistence.

        Default: in-memory MemorySaver (suitable for single-container use and
        tests).  Override in a subclass or inject a postgres-backed saver for
        cross-container persistence:

            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
            saver = await AsyncPostgresSaver.from_conn_string(settings.database_url)
            await saver.setup()
            return saver
        """
        return MemorySaver()

    def _build_graph(self) -> StateGraph | None:
        """
        Construct and compile the LangGraph for this agent.

        Returns None when the OpenAI API key is absent so that the agent
        degrades gracefully to a plain event processor.
        """
        if not settings.openai_api_key:
            logger.warning(
                "[trace] llm_disabled agent=%s reason=missing_openai_api_key",
                self.agent_name,
            )
            return None

        llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0,
            api_key=settings.openai_api_key,
        )

        llm_with_tools = llm.bind_tools(self.tools) if self.tools else llm

        # Capture SYSTEM_PROMPT for closure (avoids late-binding issues)
        system_prompt = self.SYSTEM_PROMPT

        def _chatbot(state: _AgentState) -> dict:
            messages = list(state["messages"])
            if system_prompt and (
                not messages or getattr(messages[0], "type", None) != "system"
            ):
                from langchain_core.messages import SystemMessage

                messages = [SystemMessage(content=system_prompt)] + messages
            return {"messages": [llm_with_tools.invoke(messages)]}

        builder: StateGraph = StateGraph(_AgentState)
        builder.add_node("chatbot", _chatbot)
        builder.add_edge(START, "chatbot")

        if self.tools:
            builder.add_node("tools", ToolNode(self.tools))
            builder.add_conditional_edges("chatbot", tools_condition)
            builder.add_edge("tools", "chatbot")

        return builder.compile(checkpointer=self._get_checkpointer())

    @property
    def graph(self) -> StateGraph | None:
        """Lazily built LangGraph instance."""
        if self._graph is None:
            self._graph = self._build_graph()
        return self._graph

    # ── LLM invocation helpers ─────────────────────────────────────────────────

    def _format_event(self, event_data: dict[str, Any]) -> str:
        """
        Convert an event_data dict into a user-facing message string.

        Override this method in subclasses to customise how telemetry events
        are presented to the LLM.
        """
        return json.dumps(event_data, default=str)

    async def invoke_llm(
        self,
        event_data: dict[str, Any],
        thread_id: str | None = None,
    ) -> str | None:
        """
        Run the LangGraph on a single event and return the LLM's final reply.

        Args:
            event_data: Raw event dict consumed from Redis.
            thread_id:  Checkpointer thread key.  Defaults to the event's
                        trip_id so that all turns for the same trip share
                        conversation history.

        Returns:
            The final assistant message as a string, or None if the LLM is
            not configured.
        """
        if self.graph is None:
            return None

        meta = _extract_event_meta(event_data)
        thread_id = thread_id or meta["trip_id"]
        config = {"configurable": {"thread_id": thread_id}}

        user_message = self._format_event(event_data)
        response = await self.graph.ainvoke(
            {"messages": [{"role": "user", "content": user_message}]},
            config=config,
        )

        last_msg = response["messages"][-1]
        if isinstance(last_msg.content, list):
            return "".join(
                block.get("text", "")
                for block in last_msg.content
                if isinstance(block, dict) and block.get("type") == "text"
            )
        return str(last_msg.content)

    # ── Abstract interface ─────────────────────────────────────────────────────

    @abstractmethod
    async def process_event(self, event_data: dict[str, Any]) -> dict[str, Any] | None:
        """
        Business logic for the specific agent.
        Returns a dictionary to be published, or None to skip publishing.
        """

    # ── Event loop ─────────────────────────────────────────────────────────────

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
