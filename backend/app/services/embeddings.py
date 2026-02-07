"""Embedding service using Hugging Face Inference API or local sentence-transformers."""

from __future__ import annotations

import logging
import os
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Hugging Face Inference API settings (updated URL - router.huggingface.co)
HF_API_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2/pipeline/feature-extraction"
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")

# Local model instance (only used if HF_API_TOKEN not set)
_model = None
_use_api = bool(HF_API_TOKEN)


def load_model():
    """
    Initialize the embedding service.
    Uses Hugging Face API if HF_API_TOKEN is set (for low-memory environments).
    Falls back to local model for development.
    """
    global _model, _use_api
    
    if HF_API_TOKEN:
        logger.info("Using Hugging Face Inference API for embeddings (low memory mode)")
        _use_api = True
        return None
    
    # Local mode - load sentence-transformers
    logger.info("Loading local embedding model: %s ...", settings.embedding_model_name)
    from sentence_transformers import SentenceTransformer
    _model = SentenceTransformer(settings.embedding_model_name)
    logger.info("Embedding model loaded successfully (dim=%d)", _model.get_sentence_embedding_dimension())
    _use_api = False
    return _model


def get_model():
    """Get the loaded model instance. Returns None if using API mode."""
    return _model


def _call_hf_api(texts: list[str], retries: int = 3) -> list[list[float]]:
    """Call Hugging Face Inference API for embeddings with retry logic."""
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    for attempt in range(retries):
        try:
            with httpx.Client(timeout=120) as client:
                response = client.post(
                    HF_API_URL,
                    headers=headers,
                    json={"inputs": texts, "options": {"wait_for_model": True}}
                )
                response.raise_for_status()
                result = response.json()
                
                # HF API might return an error dict instead of embeddings
                if isinstance(result, dict) and "error" in result:
                    logger.warning("HF API error (attempt %d): %s", attempt + 1, result["error"])
                    if attempt < retries - 1:
                        import time
                        time.sleep(5)  # Wait before retry
                        continue
                    raise RuntimeError(f"HF API error: {result['error']}")
                
                return result
        except httpx.TimeoutException:
            logger.warning("HF API timeout (attempt %d/%d)", attempt + 1, retries)
            if attempt < retries - 1:
                import time
                time.sleep(3)
                continue
            raise
        except Exception as e:
            logger.error("HF API error (attempt %d): %s", attempt + 1, e)
            if attempt < retries - 1:
                import time
                time.sleep(3)
                continue
            raise
    
    raise RuntimeError("HF API failed after all retries")


def encode_text(text: str) -> list[float]:
    """
    Generate a 384-dimensional embedding vector for the given text.

    Args:
        text: Input text in any supported language (Hebrew, English, etc.)

    Returns:
        List of 384 floats representing the text embedding.
    """
    if _use_api:
        result = _call_hf_api([text])
        return result[0]
    
    if _model is None:
        raise RuntimeError("Embedding model not loaded. Call load_model() first.")
    embedding = _model.encode(text, normalize_embeddings=True)
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
    if _use_api:
        # Process in batches to avoid API limits
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = _call_hf_api(batch)
            all_embeddings.extend(embeddings)
            logger.info("Processed batch %d-%d via HF API", i, i + len(batch))
        return all_embeddings
    
    if _model is None:
        raise RuntimeError("Embedding model not loaded. Call load_model() first.")
    embeddings = _model.encode(texts, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=True)
    return [emb.tolist() for emb in embeddings]
