"""LLM adapter layer - provider-agnostic interface for language models."""

from backend.common.llm.adapter import LLMAdapter
from backend.common.llm.anthropic_adapter import AnthropicAdapter
from backend.common.llm.factory import load_llm
from backend.common.llm.models import (
    AnthropicModel,
    LLMConfig,
    OpenAIModel,
)
from backend.common.llm.openai_adapter import OpenAIAdapter

__all__ = [
    "LLMAdapter",
    "OpenAIAdapter",
    "AnthropicAdapter",
    "load_llm",
    "LLMConfig",
    "OpenAIModel",
    "AnthropicModel",
]
