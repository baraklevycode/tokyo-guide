"""Tests for the sections API endpoints."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client with mocked dependencies."""
    with patch("app.services.embeddings.load_model"):
        from app.main import app

        return TestClient(app)


class TestSectionsEndpoint:
    """Tests for GET /api/sections."""

    @patch("app.routers.sections.get_all_categories")
    def test_get_sections(self, mock_get_categories, client: TestClient):
        """Sections endpoint should return categories."""
        mock_get_categories.return_value = [
            {"category": "restaurants", "count": 10},
            {"category": "neighborhoods", "count": 5},
        ]

        response = client.get("/api/sections")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) == 2

    @patch("app.routers.sections.get_all_categories")
    def test_get_sections_empty(self, mock_get_categories, client: TestClient):
        """Sections endpoint should handle empty result."""
        mock_get_categories.return_value = []

        response = client.get("/api/sections")
        assert response.status_code == 200
        data = response.json()
        assert data["categories"] == []


class TestSectionContentEndpoint:
    """Tests for GET /api/section/{category}."""

    def test_invalid_category_returns_404(self, client: TestClient):
        """Invalid category should return 404."""
        response = client.get("/api/section/nonexistent_category")
        assert response.status_code == 404

    @patch("app.routers.sections.get_content_by_category")
    def test_valid_category_returns_content(self, mock_get_content, client: TestClient):
        """Valid category should return content items."""
        mock_get_content.return_value = [
            {
                "id": "test-id-1",
                "title": "Shinjuku",
                "title_hebrew": "שינג׳וקו",
                "content_hebrew": "תוכן בדיקה",
                "category": "neighborhoods",
                "subcategory": None,
                "tags": ["shopping"],
                "location_name": "Shinjuku",
                "latitude": 35.6938,
                "longitude": 139.7034,
                "price_range": None,
                "recommended_duration": None,
                "best_time_to_visit": None,
            }
        ]

        response = client.get("/api/section/neighborhoods")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title_hebrew"] == "שינג׳וקו"


class TestSearchEndpoint:
    """Tests for POST /api/search."""

    @patch("app.routers.search.keyword_search")
    def test_search_returns_results(self, mock_search, client: TestClient):
        """Search should return matching results."""
        mock_search.return_value = [
            {
                "id": "test-id-1",
                "title": "Ramen",
                "title_hebrew": "ראמן",
                "content_hebrew": "ראמן טוב",
                "category": "restaurants",
                "subcategory": None,
                "tags": ["ramen"],
                "location_name": "Shinjuku",
            }
        ]

        response = client.post("/api/search", json={"query": "ראמן"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["results"][0]["title_hebrew"] == "ראמן"

    def test_search_requires_query(self, client: TestClient):
        """Search should reject empty query."""
        response = client.post("/api/search", json={"query": ""})
        assert response.status_code == 422


class TestSuggestionsEndpoint:
    """Tests for GET /api/suggestions."""

    def test_get_suggestions(self, client: TestClient):
        """Suggestions endpoint should return a list of questions."""
        response = client.get("/api/suggestions")
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert len(data["suggestions"]) > 0
        assert all(isinstance(s, str) for s in data["suggestions"])
