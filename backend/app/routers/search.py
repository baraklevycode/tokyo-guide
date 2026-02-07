"""Search router -- keyword search and suggested questions."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.models import ContentItem, SearchRequest, SearchResponse, SuggestionsResponse
from app.services.database import keyword_search

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["search"])

# Popular suggested questions in Hebrew
SUGGESTED_QUESTIONS: list[str] = [
    "מה כדאי לאכול בטוקיו?",
    "איפה הכי כדאי לישון בטוקיו?",
    "איך להתניידד בתחבורה ציבורית בטוקיו?",
    "מה ההמלצות לקניות בטוקיו?",
    "אילו שכונות מומלצות לביקור ראשון?",
    "איפה לאכול ראמן טוב בטוקיו?",
    "מה לעשות בשיבויה?",
    "כמה עולה טיול לטוקיו?",
    "מה כדאי להביא מיפן?",
    "האם כדאי לבקר בקיוטו?",
]


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse:
    """Keyword search across content, with optional category filter."""
    try:
        results = keyword_search(query=request.query, category=request.category)
        items = [
            ContentItem(
                id=str(item["id"]),
                title=item.get("title", ""),
                title_hebrew=item.get("title_hebrew", ""),
                content_hebrew=item.get("content_hebrew", ""),
                category=item.get("category", ""),
                subcategory=item.get("subcategory"),
                tags=item.get("tags") or [],
                location_name=item.get("location_name"),
            )
            for item in results
        ]
        return SearchResponse(results=items, total=len(items))
    except Exception as e:
        logger.error("Search failed for query '%s': %s", request.query, e)
        raise HTTPException(status_code=500, detail="שגיאה בחיפוש.")


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions() -> SuggestionsResponse:
    """Return popular suggested questions for the chat widget."""
    return SuggestionsResponse(suggestions=SUGGESTED_QUESTIONS)
