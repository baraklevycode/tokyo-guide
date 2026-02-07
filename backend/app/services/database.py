"""Supabase database client wrapper."""

from __future__ import annotations

import logging
from typing import Any, Optional

from supabase import Client, create_client

from app.config import settings

logger = logging.getLogger(__name__)

# Singleton client
_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create the Supabase client singleton."""
    global _client
    if _client is None:
        if not settings.supabase_url or not settings.supabase_key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        _client = create_client(settings.supabase_url, settings.supabase_key)
        logger.info("Supabase client initialized")
    return _client


def vector_search(
    query_embedding: list[float],
    match_threshold: float = 0.5,
    match_count: int = 5,
) -> list[dict[str, Any]]:
    """
    Search for similar content using pgvector via the match_documents RPC function.

    Args:
        query_embedding: The 384-dimensional embedding vector of the query.
        match_threshold: Minimum cosine similarity score (0-1).
        match_count: Maximum number of results to return.

    Returns:
        List of matching documents with similarity scores.
    """
    client = get_supabase_client()
    try:
        result = client.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_threshold": match_threshold,
                "match_count": match_count,
            },
        ).execute()
        return result.data or []
    except Exception as e:
        logger.error("Vector search failed: %s", e)
        return []


def get_content_by_category(category: str) -> list[dict[str, Any]]:
    """Get all content items in a specific category."""
    client = get_supabase_client()
    try:
        result = (
            client.table("tokyo_content")
            .select("id, title, title_hebrew, content_hebrew, category, subcategory, tags, location_name, latitude, longitude, price_range, recommended_duration, best_time_to_visit")
            .eq("category", category)
            .order("title_hebrew")
            .execute()
        )
        return result.data or []
    except Exception as e:
        logger.error("Failed to get content for category '%s': %s", category, e)
        return []


def get_all_categories() -> list[dict[str, Any]]:
    """Get distinct categories with their item counts."""
    client = get_supabase_client()
    try:
        result = client.table("tokyo_content").select("category").execute()
        rows = result.data or []
        # Count items per category
        counts: dict[str, int] = {}
        for row in rows:
            cat = row["category"]
            counts[cat] = counts.get(cat, 0) + 1
        return [{"category": cat, "count": count} for cat, count in sorted(counts.items())]
    except Exception as e:
        logger.error("Failed to get categories: %s", e)
        return []


def keyword_search(query: str, category: Optional[str] = None) -> list[dict[str, Any]]:
    """Full-text keyword search in content."""
    client = get_supabase_client()
    try:
        q = client.table("tokyo_content").select(
            "id, title, title_hebrew, content_hebrew, category, subcategory, tags, location_name"
        )
        # Use ilike for simple keyword matching (works for Hebrew and English)
        search_pattern = f"%{query}%"
        q = q.or_(f"content_hebrew.ilike.{search_pattern},title_hebrew.ilike.{search_pattern},title.ilike.{search_pattern}")
        if category:
            q = q.eq("category", category)
        result = q.limit(20).execute()
        return result.data or []
    except Exception as e:
        logger.error("Keyword search failed for query '%s': %s", query, e)
        return []


def get_session(session_id: str) -> Optional[dict[str, Any]]:
    """Get a chat session by ID."""
    client = get_supabase_client()
    try:
        result = client.table("chat_sessions").select("*").eq("id", session_id).single().execute()
        return result.data
    except Exception:
        return None


def create_session(user_id: str = "anonymous", platform: str = "web") -> str:
    """Create a new chat session and return its ID."""
    client = get_supabase_client()
    result = client.table("chat_sessions").insert(
        {"user_id": user_id, "platform": platform, "messages": []}
    ).execute()
    return result.data[0]["id"]


def update_session_messages(session_id: str, messages: list[dict[str, str]]) -> None:
    """Update the messages in a chat session."""
    client = get_supabase_client()
    try:
        client.table("chat_sessions").update(
            {"messages": messages, "updated_at": "now()"}
        ).eq("id", session_id).execute()
    except Exception as e:
        logger.error("Failed to update session '%s': %s", session_id, e)
