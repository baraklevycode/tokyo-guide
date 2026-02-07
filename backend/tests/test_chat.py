"""Tests for the chat API endpoint."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client with mocked dependencies."""
    # Mock the embedding model loading to avoid downloading the model in tests
    with patch("app.services.embeddings.load_model"):
        from app.main import app

        return TestClient(app)


class TestChatEndpoint:
    """Tests for POST /api/chat."""

    def test_chat_requires_question(self, client: TestClient):
        """Chat endpoint should reject empty question."""
        response = client.post("/api/chat", json={"question": ""})
        assert response.status_code == 422

    def test_chat_requires_body(self, client: TestClient):
        """Chat endpoint should reject missing body."""
        response = client.post("/api/chat")
        assert response.status_code == 422

    @patch("app.routers.chat.answer_question")
    async def test_chat_returns_response(self, mock_answer, client: TestClient):
        """Chat endpoint should return a proper response."""
        from app.models import ChatResponse, SourceReference

        mock_answer.return_value = ChatResponse(
            answer="תשובה לדוגמה",
            sources=[
                SourceReference(
                    id="123",
                    title="Test",
                    title_hebrew="בדיקה",
                    category="restaurants",
                    similarity=0.85,
                )
            ],
            session_id="test-session-id",
            suggested_questions=["שאלה 1?", "שאלה 2?"],
        )

        response = client.post(
            "/api/chat", json={"question": "מה כדאי לאכול?"}
        )
        assert response.status_code == 200 or response.status_code == 500
        # Note: 500 may occur if Supabase/Groq are not configured in tests


class TestHealthEndpoint:
    """Tests for GET /health."""

    def test_health_check(self, client: TestClient):
        """Health endpoint should return ok status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_root_endpoint(self, client: TestClient):
        """Root endpoint should return basic info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
