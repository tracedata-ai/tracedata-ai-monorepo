"""Orchestrator package (lazy `OrchestratorAgent` so `prompts` stays lightweight)."""

from __future__ import annotations

__all__ = ["OrchestratorAgent"]


def __getattr__(name: str):
    if name == "OrchestratorAgent":
        from agents.orchestrator.agent import OrchestratorAgent

        return OrchestratorAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
