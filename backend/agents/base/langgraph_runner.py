"""
Explicit LangGraph tool loop (StateGraph + ToolNode + tools_condition).

Shared by domain agents. LLM reasoning and tool calls occur only inside this graph.
"""

from __future__ import annotations

import json
from typing import Annotated, Any, List, TypedDict

from langchain_core.messages import AnyMessage, BaseMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


class ToolLoopState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]


def build_tool_loop_graph(
    llm: Any,
    tools: list,
    *,
    checkpointer: Any | None = None,
):
    """
    Build and compile: chatbot -> tools_condition -> ToolNode -> chatbot.

    The chatbot node is the only place the bound LLM is invoked (notebook pattern).
    """
    llm_with_tools = llm.bind_tools(tools)

    def chatbot(state: ToolLoopState) -> dict[str, list[BaseMessage]]:
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    builder = StateGraph(ToolLoopState)
    builder.add_node("chatbot", chatbot)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "chatbot")
    builder.add_conditional_edges("chatbot", tools_condition)
    builder.add_edge("tools", "chatbot")

    cp = checkpointer if checkpointer is not None else MemorySaver()
    return builder.compile(checkpointer=cp)


def parse_json_from_last_ai_message(result: dict[str, Any]) -> dict[str, Any] | None:
    """Extract JSON from the last AI/assistant message (skip tool messages)."""
    messages = result.get("messages") or []
    for msg in reversed(messages):
        role = getattr(msg, "type", None) or getattr(msg, "role", None)
        if role not in ("ai", "assistant"):
            continue
        content = getattr(msg, "content", None)
        if content is None:
            continue
        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            parts: list[str] = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(str(block.get("text", "")))
                elif isinstance(block, str):
                    parts.append(block)
            text = "".join(parts)
        else:
            text = str(content)
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            continue
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            continue
    return None
