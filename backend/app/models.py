"""Pydantic models for API request/response schemas."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ── Request models ──────────────────────────────────────────────────────────


class ChatRequest(BaseModel):
    """Request body for the /api/chat endpoint."""

    question: str = Field(..., min_length=1, max_length=2000, description="User question in Hebrew or English")
    session_id: Optional[str] = Field(None, description="Existing chat session ID for conversation continuity")


class SearchRequest(BaseModel):
    """Request body for the /api/search endpoint."""

    query: str = Field(..., min_length=1, max_length=500, description="Search query text")
    category: Optional[str] = Field(None, description="Optional category filter")


# ── Response models ─────────────────────────────────────────────────────────


class SourceReference(BaseModel):
    """A source document referenced in the chat answer."""

    id: str
    title: str
    title_hebrew: str
    category: str
    similarity: float


class ChatResponse(BaseModel):
    """Response body for the /api/chat endpoint."""

    answer: str
    sources: list[SourceReference]
    session_id: str
    suggested_questions: list[str]


class ContentItem(BaseModel):
    """A single piece of Tokyo guide content."""

    id: str
    title: str
    title_hebrew: str
    content: str = ""
    content_hebrew: str = ""
    category: str
    subcategory: Optional[str] = None
    tags: list[str] = []
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    price_range: Optional[str] = None
    recommended_duration: Optional[str] = None
    best_time_to_visit: Optional[str] = None


class CategoryInfo(BaseModel):
    """Category with item count."""

    category: str
    label_hebrew: str
    count: int
    icon: str


class SectionsResponse(BaseModel):
    """Response body for GET /api/sections."""

    categories: list[CategoryInfo]


class SearchResponse(BaseModel):
    """Response body for POST /api/search."""

    results: list[ContentItem]
    total: int


class SuggestionsResponse(BaseModel):
    """Response body for GET /api/suggestions."""

    suggestions: list[str]


class HealthResponse(BaseModel):
    """Response body for GET /health."""

    status: str
    version: str
