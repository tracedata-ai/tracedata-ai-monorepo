"""Notebook-style LangGraph pipeline for sentiment analysis."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, TypedDict

from langgraph.graph import END, StateGraph


class SentimentState(TypedDict, total=False):
    driver_id: str
    submission_id: str
    timestamp: str
    text: str
    current_scores: dict[str, float]
    current_embedding: list[float]
    history_rows: list[dict[str, Any]]
    window_stats: dict[str, float]
    trend: dict[str, str]
    risk_level: float
    explanation: str
    final_output: dict[str, Any]


def build_sentiment_graph(
    *,
    score_current: Callable[[SentimentState], Awaitable[dict[str, Any]]],
    load_history: Callable[[SentimentState], Awaitable[dict[str, Any]]],
    analyze_window: Callable[[SentimentState], dict[str, Any]],
    explain: Callable[[SentimentState], Awaitable[dict[str, Any]]],
    assemble_output: Callable[[SentimentState], dict[str, Any]],
):
    """Compile the linear notebook pipeline into a LangGraph graph."""
    builder = StateGraph(SentimentState)
    builder.add_node("score_current", score_current)
    builder.add_node("load_history", load_history)
    builder.add_node("analyze_window", analyze_window)
    builder.add_node("explain", explain)
    builder.add_node("assemble_output", assemble_output)

    builder.set_entry_point("score_current")
    builder.add_edge("score_current", "load_history")
    builder.add_edge("load_history", "analyze_window")
    builder.add_edge("analyze_window", "explain")
    builder.add_edge("explain", "assemble_output")
    builder.add_edge("assemble_output", END)
    return builder.compile()
