"""Embedding service using sentence-transformers for multilingual text."""

from __future__ import annotations

import logging
from typing import Optional

from sentence_transformers import SentenceTransformer

from app.config import settings

logger = logging.getLogger(__name__)

# Singleton model instance (loaded once at startup)
_model: Optional[SentenceTransformer] = None


def load_model() -> SentenceTransformer:
    """
    Load the sentence-transformers model.
    Called once during application startup via the lifespan handler.
    Model: paraphrase-multilingual-MiniLM-L12-v2
      - Supports 50+ languages including Hebrew
      - Output dimension: 384
      - Size: ~120MB
    """
    global _model
    if _model is None:
        logger.info("Loading embedding model: %s ...", settings.embedding_model_name)
        _model = SentenceTransformer(settings.embedding_model_name)
        logger.info("Embedding model loaded successfully (dim=%d)", _model.get_sentence_embedding_dimension())
    return _model


def get_model() -> SentenceTransformer:
    """Get the loaded model instance. Raises if not yet loaded."""
    if _model is None:
        raise RuntimeError("Embedding model not loaded. Call load_model() first.")
    return _model


def encode_text(text: str) -> list[float]:
    """
    Generate a 384-dimensional embedding vector for the given text.

    Args:
        text: Input text in any supported language (Hebrew, English, etc.)

    Returns:
        List of 384 floats representing the text embedding.
    """
    model = get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def encode_batch(texts: list[str], batch_size: int = 32) -> list[list[float]]:
    """
    Generate embeddings for a batch of texts.

    Args:
        texts: List of input texts.
        batch_size: Number of texts to process at once.

    Returns:
        List of embedding vectors.
    """
    model = get_model()
    embeddings = model.encode(texts, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=True)
    return [emb.tolist() for emb in embeddings]
