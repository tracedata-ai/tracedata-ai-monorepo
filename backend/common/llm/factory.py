"""LLM factory for provider-agnostic model loading."""

from common.llm.anthropic_adapter import AnthropicAdapter
from common.llm.models import AnthropicModel, LLMConfig, OpenAIModel
from common.llm.openai_adapter import OpenAIAdapter


def _infer_provider_from_model(model: OpenAIModel | AnthropicModel) -> str:
    """Infer provider from model enum."""
    if isinstance(model, OpenAIModel):
        return "openai"
    return "anthropic"


def load_llm(model: OpenAIModel | AnthropicModel) -> LLMConfig:
    """Factory that accepts a model enum and returns a configured adapter.

    Examples:
        >>> config = load_llm(OpenAIModel.GPT_4O)
        >>> llm = config.adapter.get_chat_model()

        >>> config = load_llm(AnthropicModel.CLAUDE_35_SONNET_20241022)
        >>> llm = config.adapter.get_chat_model()
    """
    from dotenv import load_dotenv

    load_dotenv()

    resolved_provider = _infer_provider_from_model(model)

    if resolved_provider == "openai":
        adapter = OpenAIAdapter(model=model)
    else:
        adapter = AnthropicAdapter(model=model)

    return LLMConfig(
        provider=resolved_provider,
        model=adapter.model.value,
        adapter=adapter,
    )
