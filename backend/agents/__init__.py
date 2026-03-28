"""
TraceData Backend — Agents Package.

Contains the AI agents co-located in this container:
  - base:         Thick BaseAgent class (LangGraph + OpenAI) — inherit to build agents
  - orchestrator: Routes user requests to specialist agents
  - feedback:     Generates driver coaching feedback

All agents extend ``BaseAgent`` — subclass it and set ``SYSTEM_PROMPT`` +
``tools`` to create a new agent with full LLM + memory + tool support.
"""

from agents.base import AgentState, BaseAgent
from agents.feedback import FeedbackAgent
from agents.orchestrator import OrchestratorAgent

__all__ = [
    "AgentState",
    "BaseAgent",
    "FeedbackAgent",
    "OrchestratorAgent",
]
