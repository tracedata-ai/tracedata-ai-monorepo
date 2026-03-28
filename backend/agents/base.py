"""
TraceData — BaseAgent
=====================
A *thick* base class that wires together the full LangGraph + OpenAI stack so
that concrete agents only need to:

    1. Inherit ``BaseAgent``.
    2. Override ``SYSTEM_PROMPT`` (str) — the agent's persona / rules.
    3. Override ``tools`` (list) — zero or more ``@tool``-decorated callables.
    4. Optionally override ``model``, ``temperature``, or ``enable_web_search``.

Everything else — LLM, memory (MemorySaver), tool binding, StateGraph wiring,
and the public ``invoke`` / ``stream`` methods — is handled here.

Usage example
-------------
::

    from langchain_core.tools import tool
    from agents.base import BaseAgent

    @tool
    def estimate_cost(days: int, travelers: int) -> dict:
        \"\"\"Estimate rough trip cost in SGD.\"\"\"
        total = days * travelers * 200
        return {"total_sgd": total}

    class TravelAgent(BaseAgent):
        SYSTEM_PROMPT = \"\"\"You are a travel planning agent.
        Use estimate_cost when the user asks about budget.\"\"\"
        tools = [estimate_cost]

    agent = TravelAgent()
    response = agent.invoke("Plan a 2-day Tokyo trip for 2 adults.", thread_id="t1")
    print(response["messages"][-1].content)

Thread-safety
-------------
Each ``BaseAgent`` instance keeps its own ``MemorySaver``.  If you need a
shared persistent store across processes, replace the ``checkpointer``
constructor kwarg with a ``LangGraph`` persistent checkpointer (e.g. Postgres).
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from typing import Annotated, Any

from langchain_core.messages import AnyMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

# ---------------------------------------------------------------------------
# Graph state shared by every agent
# ---------------------------------------------------------------------------


class AgentState(TypedDict):
    """Minimal LangGraph state.  ``add_messages`` makes the list append-only
    and compatible with iterative tool-call loops."""

    messages: Annotated[list[AnyMessage], add_messages]


# ---------------------------------------------------------------------------
# Thick base class
# ---------------------------------------------------------------------------


class BaseAgent:
    """Full-featured LangGraph + OpenAI agent base class.

    Subclass this and set ``SYSTEM_PROMPT`` (and optionally ``tools``,
    ``model``, ``temperature``, ``enable_web_search``).  Then call
    ``agent.invoke(user_message, thread_id=...)`` or
    ``agent.stream(user_message, thread_id=...)``.

    Class attributes
    ----------------
    SYSTEM_PROMPT : str
        The system message prepended to every new conversation thread.
        Concrete subclasses **must** set this.
    tools : list[BaseTool]
        ``@tool``-decorated callables the LLM may invoke.  Defaults to ``[]``.
    model : str
        OpenAI model name.  Defaults to ``"gpt-4.1-mini"``.
    temperature : float
        Sampling temperature.  Defaults to ``0`` for deterministic output.
    enable_web_search : bool
        When ``True``, the OpenAI ``web_search_preview`` built-in tool is
        added alongside ``tools``.  Defaults to ``False``.
    """

    # ---- subclass-facing knobs ------------------------------------------- #

    SYSTEM_PROMPT: str = ""
    tools: list[BaseTool] = []
    model: str = "gpt-4.1-mini"
    temperature: float = 0
    enable_web_search: bool = False

    # ---- lifecycle -------------------------------------------------------- #

    def __init__(self, checkpointer: Any | None = None) -> None:
        """Build the LangGraph graph and compile it.

        Parameters
        ----------
        checkpointer:
            Optional LangGraph checkpointer.  Defaults to an in-process
            ``MemorySaver`` (good for single-process / dev use).  Supply a
            persistent checkpointer (e.g. ``AsyncPostgresSaver``) for
            production multi-process deployments.
        """
        if not self.SYSTEM_PROMPT:
            raise ValueError(
                f"{type(self).__name__} must define a non-empty SYSTEM_PROMPT."
            )

        self._checkpointer = checkpointer or MemorySaver()
        self._graph = self._build_graph()

    # ---- public API ------------------------------------------------------- #

    def invoke(
        self,
        user_message: str,
        *,
        thread_id: str | None = None,
        extra_config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run the agent and return the full final state.

        Parameters
        ----------
        user_message:
            The human turn to process.
        thread_id:
            Identifies the conversation thread for memory continuity.  A new
            UUID is generated if not provided (stateless single-turn call).
        extra_config:
            Optional extra keys merged into the ``configurable`` dict passed to
            the graph (e.g. ``{"recursion_limit": 20}``).

        Returns
        -------
        dict
            The final LangGraph state (``{"messages": [...]}``).  The last
            assistant message is at ``result["messages"][-1]``.
        """
        config = self._build_config(thread_id, extra_config)
        initial_state = self._build_initial_state(user_message, thread_id)
        return self._graph.invoke(initial_state, config=config)

    def stream(
        self,
        user_message: str,
        *,
        thread_id: str | None = None,
        extra_config: dict[str, Any] | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Stream intermediate state chunks as the agent processes a turn.

        Yields each graph node's output dict as it becomes available.
        Useful for SSE / WebSocket streaming endpoints.

        Parameters
        ----------
        user_message:
            The human turn to process.
        thread_id:
            Conversation thread identifier (same semantics as ``invoke``).
        extra_config:
            Optional extra keys merged into the graph config.

        Yields
        ------
        dict
            Intermediate state chunk from each graph node.
        """
        config = self._build_config(thread_id, extra_config)
        initial_state = self._build_initial_state(user_message, thread_id)
        yield from self._graph.stream(initial_state, config=config)

    # ---- graph construction ----------------------------------------------- #

    def _build_graph(self) -> Any:
        """Wire up the LangGraph StateGraph and return the compiled graph."""
        bound_tools = list(self.tools)
        all_tool_specs: list[Any] = []

        if self.enable_web_search:
            all_tool_specs.append({"type": "web_search_preview"})

        all_tool_specs.extend(bound_tools)

        llm = ChatOpenAI(model=self.model, temperature=self.temperature)
        llm_with_tools = llm.bind_tools(all_tool_specs) if all_tool_specs else llm

        def _chatbot_node(state: AgentState) -> dict[str, Any]:
            """Core LLM node — prepends system prompt on the first turn."""
            messages = list(state["messages"])

            # Only prepend the system prompt when it is not already present so
            # that multi-turn threads don't accumulate duplicate system messages.
            if self.SYSTEM_PROMPT and not any(
                isinstance(m, SystemMessage) for m in messages
            ):
                messages = [SystemMessage(content=self.SYSTEM_PROMPT)] + messages

            return {"messages": [llm_with_tools.invoke(messages)]}

        builder = StateGraph(AgentState)
        builder.add_node("chatbot", _chatbot_node)

        if bound_tools:
            builder.add_node("tools", ToolNode(bound_tools))
            builder.add_edge(START, "chatbot")
            builder.add_conditional_edges("chatbot", tools_condition)
            builder.add_edge("tools", "chatbot")
        else:
            builder.add_edge(START, "chatbot")

        return builder.compile(checkpointer=self._checkpointer)

    # ---- helpers ---------------------------------------------------------- #

    def _build_config(
        self,
        thread_id: str | None,
        extra_config: dict[str, Any] | None,
    ) -> dict[str, Any]:
        tid = thread_id or str(uuid.uuid4())
        configurable: dict[str, Any] = {"thread_id": tid}
        if extra_config:
            configurable.update(extra_config)
        return {"configurable": configurable}

    def _build_initial_state(
        self,
        user_message: str,
        thread_id: str | None,
    ) -> dict[str, Any]:
        """Return the state dict to pass to the graph.

        On the **first turn** of a new thread the system prompt is injected by
        ``_chatbot_node``; subsequent turns only need the user message so that
        memory is maintained via the checkpointer without duplicating the
        system message.
        """
        return {"messages": [{"role": "user", "content": user_message}]}

    # ---- convenience ------------------------------------------------------ #

    @property
    def graph(self) -> Any:
        """Expose the compiled LangGraph graph for advanced usage (e.g. drawing
        the Mermaid diagram)."""
        return self._graph
