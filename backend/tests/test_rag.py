"""Tests for the RAG pipeline and embedding services."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestEmbeddingsService:
    """Tests for the embeddings service."""

    @patch("app.services.embeddings.SentenceTransformer")
    def test_load_model(self, mock_transformer_class):
        """Loading the model should create a SentenceTransformer instance."""
        from app.services.embeddings import load_model
        import app.services.embeddings as emb_module

        # Reset singleton
        emb_module._model = None

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer_class.return_value = mock_model

        result = load_model()
        assert result is mock_model
        mock_transformer_class.assert_called_once()

        # Cleanup
        emb_module._model = None

    @patch("app.services.embeddings._model")
    def test_encode_text(self, mock_model):
        """encode_text should return a list of floats."""
        import numpy as np
        from app.services.embeddings import encode_text
        import app.services.embeddings as emb_module

        mock_model_instance = MagicMock()
        mock_model_instance.encode.return_value = np.zeros(384)
        emb_module._model = mock_model_instance

        result = encode_text("בדיקה")
        assert isinstance(result, list)
        assert len(result) == 384
        mock_model_instance.encode.assert_called_once()

        # Cleanup
        emb_module._model = None


class TestGroqClient:
    """Tests for the Groq client wrapper (openai/gpt-oss-20b, non-streaming)."""

    @patch("app.services.groq_client.Groq")
    def test_generate_response(self, mock_groq_class):
        """generate_response should call Groq API and return content text."""
        from app.services.groq_client import generate_response
        import app.services.groq_client as groq_module

        # Reset singleton
        groq_module._client = None

        # Mock Groq client with non-streaming response
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="תשובה לדוגמה"))]
        mock_client.chat.completions.create.return_value = mock_response

        with patch("app.services.groq_client.settings") as mock_settings:
            mock_settings.groq_api_key = "test-key"
            mock_settings.groq_model_name = "openai/gpt-oss-20b"
            mock_settings.rag_temperature = 1.0
            mock_settings.rag_max_completion_tokens = 8192
            mock_settings.rag_top_p = 1.0
            mock_settings.rag_reasoning_effort = "medium"

            result = generate_response(
                context="מידע בדיקה",
                question="שאלה?",
            )

        assert result == "תשובה לדוגמה"

        # Verify correct parameters were passed
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["stream"] is False
        assert call_kwargs["model"] == "openai/gpt-oss-20b"
        assert call_kwargs["reasoning_effort"] == "medium"
        assert call_kwargs["max_completion_tokens"] == 8192

        # Cleanup
        groq_module._client = None

    @patch("app.services.groq_client.Groq")
    def test_generate_response_handles_error(self, mock_groq_class):
        """generate_response should handle API errors gracefully."""
        from app.services.groq_client import generate_response
        import app.services.groq_client as groq_module

        groq_module._client = None

        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API error")

        with patch("app.services.groq_client.settings") as mock_settings:
            mock_settings.groq_api_key = "test-key"
            mock_settings.groq_model_name = "openai/gpt-oss-20b"
            mock_settings.rag_temperature = 1.0
            mock_settings.rag_max_completion_tokens = 8192
            mock_settings.rag_top_p = 1.0
            mock_settings.rag_reasoning_effort = "medium"

            result = generate_response(
                context="מידע",
                question="שאלה?",
            )

        assert "שגיאה" in result

        groq_module._client = None
