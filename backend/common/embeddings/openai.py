"""OpenAI embedding helpers shared across agents."""

from __future__ import annotations

import os
from typing import Sequence

from langchain_openai import OpenAIEmbeddings

DEFAULT_OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_OPENAI_EMBEDDING_DIMENSIONS = 1536


def vector_to_pgvector_literal(values: Sequence[float]) -> str:
    """Serialize floats into the textual pgvector literal accepted by Postgres."""
    return "[" + ",".join(f"{float(v):.8f}" for v in values) + "]"


class OpenAIEmbeddingService:
    """Thin async wrapper around ``OpenAIEmbeddings`` for reuse across agents."""

    def __init__(
        self,
        *,
        model: str = DEFAULT_OPENAI_EMBEDDING_MODEL,
        dimensions: int = DEFAULT_OPENAI_EMBEDDING_DIMENSIONS,
    ) -> None:
        if not os.getenv("OPENAI_API_KEY"):
            raise OSError(
                "OPENAI_API_KEY not found in environment. "
                "Set it before using OpenAI embeddings."
            )

        self.model = model
        self.dimensions = dimensions
        self._client = OpenAIEmbeddings(model=model, dimensions=dimensions)

    async def embed_text(self, text: str) -> list[float]:
        """Return one embedding vector for the provided text."""
        if not text.strip():
            return [0.0] * self.dimensions
        vector = await self._client.aembed_query(text)
        return [float(v) for v in vector]
