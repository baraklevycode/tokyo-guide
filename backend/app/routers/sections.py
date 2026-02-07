"""Sections router -- browse content by category."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.models import CategoryInfo, ContentItem, SectionsResponse
from app.services.database import get_all_categories, get_content_by_category

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["sections"])

# Category metadata: Hebrew labels and icons
CATEGORY_META: dict[str, dict[str, str]] = {
    "neighborhoods": {"label_hebrew": "שכונות ואזורים", "icon": "🏘️"},
    "attractions": {"label_hebrew": "אטרקציות וציוני דרך", "icon": "⛩️"},
    "restaurants": {"label_hebrew": "מסעדות ואוכל", "icon": "🍜"},
    "hotels": {"label_hebrew": "מלונות ולינה", "icon": "🏨"},
    "transportation": {"label_hebrew": "תחבורה", "icon": "🚃"},
    "shopping": {"label_hebrew": "קניות", "icon": "🛍️"},
    "cultural_experiences": {"label_hebrew": "חוויות תרבותיות", "icon": "🎎"},
    "day_trips": {"label_hebrew": "טיולי יום", "icon": "🗻"},
    "practical_tips": {"label_hebrew": "טיפים שימושיים", "icon": "💡"},
    "itinerary": {"label_hebrew": "הצעות למסלולים", "icon": "🗺️"},
}


@router.get("/sections", response_model=SectionsResponse)
async def get_sections() -> SectionsResponse:
    """Get all content categories with item counts."""
    try:
        raw_categories = get_all_categories()
        categories = []
        for item in raw_categories:
            cat = item["category"]
            meta = CATEGORY_META.get(cat, {"label_hebrew": cat, "icon": "📌"})
            categories.append(
                CategoryInfo(
                    category=cat,
                    label_hebrew=meta["label_hebrew"],
                    count=item["count"],
                    icon=meta["icon"],
                )
            )
        return SectionsResponse(categories=categories)
    except Exception as e:
        logger.error("Failed to get sections: %s", e)
        raise HTTPException(status_code=500, detail="שגיאה בטעינת הקטגוריות.")


@router.get("/section/{category}", response_model=list[ContentItem])
async def get_section_content(category: str) -> list[ContentItem]:
    """Get all content items for a specific category."""
    if category not in CATEGORY_META:
        raise HTTPException(status_code=404, detail=f"קטגוריה '{category}' לא נמצאה.")

    try:
        items = get_content_by_category(category)
        return [
            ContentItem(
                id=str(item["id"]),
                title=item.get("title", ""),
                title_hebrew=item.get("title_hebrew", ""),
                content_hebrew=item.get("content_hebrew", ""),
                category=item.get("category", category),
                subcategory=item.get("subcategory"),
                tags=item.get("tags") or [],
                location_name=item.get("location_name"),
                latitude=item.get("latitude"),
                longitude=item.get("longitude"),
                price_range=item.get("price_range"),
                recommended_duration=item.get("recommended_duration"),
                best_time_to_visit=item.get("best_time_to_visit"),
            )
            for item in items
        ]
    except Exception as e:
        logger.error("Failed to get content for category '%s': %s", category, e)
        raise HTTPException(status_code=500, detail="שגיאה בטעינת התוכן.")
