"""Embedding service using Hugging Face Inference API or local sentence-transformers."""

from __future__ import annotations

import logging
import os
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

# Hugging Face API settings
HF_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Module state (initialized in load_model)
_model = None
_hf_client = None
_use_api = False


def load_model():
    """
    Initialize the embedding service.
    Uses Hugging Face API if HF_API_TOKEN is set (for low-memory environments).
    Falls back to local model for development.
    """
    global _model, _hf_client, _use_api
    
    # Check token at runtime, not module load time
    hf_token = os.getenv("HF_API_TOKEN", "")
    
    if hf_token:
        logger.info("Using Hugging Face Inference API for embeddings (low memory mode)")
        from huggingface_hub import InferenceClient
        _hf_client = InferenceClient(provider="hf-inference", api_key=hf_token)
        _use_api = True
        logger.info("HF InferenceClient initialized successfully")
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
    import time
    
    for attempt in range(retries):
        try:
            # Use the HuggingFace Hub client
            if len(texts) == 1:
                result = _hf_client.feature_extraction(texts[0], model=HF_MODEL)
                # Convert numpy float32 to Python float for JSON serialization
                return [[float(x) for x in result]]
            else:
                # Process multiple texts
                results = []
                for text in texts:
                    embedding = _hf_client.feature_extraction(text, model=HF_MODEL)
                    # Convert numpy float32 to Python float
                    results.append([float(x) for x in embedding])
                return results
                
        except Exception as e:
            error_msg = str(e)
            logger.warning("HF API error (attempt %d/%d): %s", attempt + 1, retries, error_msg)
            
            if attempt < retries - 1:
                wait_time = 5 * (attempt + 1)  # Exponential backoff
                logger.info("Retrying in %d seconds...", wait_time)
                time.sleep(wait_time)
                continue
            raise RuntimeError(f"HF API failed after {retries} attempts: {error_msg}")


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
