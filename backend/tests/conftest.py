"""
Shared pytest fixtures for the TraceData backend test suite.
"""

import os

import pytest


@pytest.fixture(autouse=True)
def _set_dummy_openai_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set a placeholder OPENAI_API_KEY so ChatOpenAI can be *constructed*
    in offline tests without raising an error.

    This key is never used to make real API calls — tests that exercise
    agent graph *invocation* must mock the LLM separately.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-placeholder-key")
