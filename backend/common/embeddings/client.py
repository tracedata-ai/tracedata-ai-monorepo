"""Thin async wrapper around OpenAI text-embedding-3-small.

langchain-openai is already a project dependency, so no new package required.
Returns None on failure so callers can skip storage without crashing.
"""

import logging

from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)

_model: OpenAIEmbeddings | None = None


def _get_model() -> OpenAIEmbeddings:
    global _model
    if _model is None:
        _model = OpenAIEmbeddings(model="text-embedding-3-small")
    return _model


async def embed_text(text: str) -> list[float] | None:
    if not text or not text.strip():
        return None
    try:
        return await _get_model().aembed_query(text.strip())
    except Exception as exc:
        logger.warning("Embedding generation failed: %s", exc)
        return None
