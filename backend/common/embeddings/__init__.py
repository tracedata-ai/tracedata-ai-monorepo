"""Shared embedding helpers for agents that need vector workflows."""

from common.embeddings.openai import (
    DEFAULT_OPENAI_EMBEDDING_DIMENSIONS,
    DEFAULT_OPENAI_EMBEDDING_MODEL,
    OpenAIEmbeddingService,
    vector_to_pgvector_literal,
)

__all__ = [
    "DEFAULT_OPENAI_EMBEDDING_DIMENSIONS",
    "DEFAULT_OPENAI_EMBEDDING_MODEL",
    "OpenAIEmbeddingService",
    "vector_to_pgvector_literal",
]
