"""
Scraper for the Ptitim Tokyo Guide blog.

Fetches the blog page at https://www.ptitim.com/tokyoguide/ and extracts
structured content sections with Hebrew text, mapped to categories.

The blog is structured with numbered H1/H2 sections:
  1/ כמה דגשים
  2/ טיפים שימושיים
  3/ איפה לישון
  4/ האיזורים (והתחנות) שאני אוהב בטוקיו
  5/ המפה הסודית
  6/ המדריך לאכילה בטוקיו
  7/ רשימת הזהב שלי
  8/ מה לקנות ביפן
  9/ המשך קריאה
  10/ הצצה לקיוטו
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from typing import Optional

import httpx
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

BLOG_URL = "https://www.ptitim.com/tokyoguide/"

# Minimum content length to include (characters)
MIN_CONTENT_LENGTH = 100


@dataclass
class ScrapedSection:
    """A parsed section from the blog."""

    title: str
    title_hebrew: str
    content: str
    content_hebrew: str
    category: str
    subcategory: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    location_name: Optional[str] = None


# Known neighborhood names with their Hebrew equivalents
NEIGHBORHOODS = {
    "shinjuku": ("Shinjuku", "שינג׳וקו"),
    "shibuya": ("Shibuya", "שיבויה"),
    "harajuku": ("Harajuku", "הראג׳וקו"),
    "ikebukuro": ("Ikebukuro", "איקבוקורו"),
    "asakusa": ("Asakusa", "אסקוסה"),
    "ueno": ("Ueno", "אואנו"),
    "ginza": ("Ginza", "גינזה"),
    "akihabara": ("Akihabara", "אקיהאברה"),
    "shimokitazawa": ("Shimokitazawa", "שימוקיטזאווה"),
    "nakameguro": ("Nakameguro", "נקמגורו"),
    "roppongi": ("Roppongi", "רופונגי"),
    "jiyugaoka": ("Jiyugaoka", "ג׳יוגאוקה"),
    "yanaka": ("Yanaka", "יאנאקה"),
    "koenji": ("Koenji", "קואנג׳י"),
    "kichijoji": ("Kichijoji", "קיצ׳יג׳וג׳י"),
    "odaiba": ("Odaiba", "אודייבה"),
    "tokyo station": ("Tokyo Station", "תחנת טוקיו"),
}

# Gold list restaurants
GOLD_LIST_RESTAURANTS = [
    "Nagi ramen", "Fu unji ramen", "Ginza Kagari", "Menya Hanabi",
    "butagumi", "Yamabe Okachimachi", "Gyukatsu Motomura", "Maguro Mart",
    "Tensuke", "Tsujihan", "shusai soba shodai", "Shinpachi Shokudo",
    "Miko Shokudo", "Coco Ichibanya", "Kitchen Nankai", "Uogashi Nihon-Ichi",
    "Kaiten Sushi Ginza Onodera", "Shouei Sushi Nakano", "Sushisho Masa",
    "Ebisu Endou", "Kosoan", "Lion cafe", "Sakurai souen", "Oiwake Dango",
    "Yoshinoya", "Shibuya morimoto", "Mentsu-dan", "Shin udon",
    "Kirimugiya Jinroku", "Menki Yashima Tomigaya", "Takamarusengyoten",
    "Hakushū Teppanyaki", "Harajuku Gyozaro", "Isomaru Suisan", "Marukou Suisan",
    "Ramen & Onigiri Eddie", "Waku Bessatsu", "Shinpachi Shokudo",
]


def _clean_text(text: str) -> str:
    """Clean up extracted text."""
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


def _extract_tags(content: str) -> list[str]:
    """Extract relevant tags from content."""
    tags = []
    tag_keywords = {
        "ראמן": "ramen", "סושי": "sushi", "טמפורה": "tempura",
        "אודון": "udon", "יקיטורי": "yakitori", "איזקאיה": "izakaya",
        "קארי": "curry", "מקדש": "temple", "פארק": "park",
        "מוזיאון": "museum", "שוק": "market", "קניות": "shopping",
        "קפה": "cafe", "בר": "bar", "מנגה": "manga", "אנימה": "anime",
    }
    for hebrew, english in tag_keywords.items():
        if hebrew in content:
            tags.append(english)
    return tags


def _detect_neighborhood(text: str) -> Optional[tuple[str, str]]:
    """Detect if text mentions a known neighborhood."""
    text_lower = text.lower()
    for key, (eng, heb) in NEIGHBORHOODS.items():
        if key in text_lower or eng.lower() in text_lower:
            return (eng, heb)
    return None


def _detect_restaurant(text: str) -> Optional[str]:
    """Detect if text mentions a known restaurant."""
    text_lower = text.lower()
    for restaurant in GOLD_LIST_RESTAURANTS:
        if restaurant.lower() in text_lower:
            return restaurant
    return None


def fetch_blog_html() -> str:
    """Fetch the blog page HTML."""
    logger.info("Fetching blog page: %s", BLOG_URL)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5,he;q=0.3",
    }
    try:
        response = httpx.get(BLOG_URL, timeout=30, follow_redirects=True, headers=headers)
        response.raise_for_status()
        logger.info("Blog page fetched (%d bytes)", len(response.text))
        return response.text
    except Exception as e:
        logger.warning("Live fetch failed (%s), trying cached file...", e)
        cache_path = os.path.join(os.path.dirname(__file__), "blog_cache.html")
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                return f.read()
        raise RuntimeError(f"Cannot fetch blog and no cache: {e}")


def parse_blog(html: str) -> list[ScrapedSection]:
    """
    Parse the blog HTML into structured sections.
    
    Strategy: Extract major topic sections and keep content together.
    Split only on main headers (H2) for neighborhoods and restaurants.
    """
    soup = BeautifulSoup(html, "lxml")
    
    content_area = soup.find("div", class_="post__content")
    if not content_area:
        content_area = soup.find("div", class_="entry-content")
    if not content_area:
        content_area = soup.find("article")
    if not content_area:
        content_area = soup.body
    
    if content_area is None:
        logger.error("Could not parse blog HTML")
        return []
    
    sections: list[ScrapedSection] = []
    
    # Strategy: Find H2 headers and collect all content until next H2
    h2_elements = content_area.find_all("h2")
    
    for i, h2 in enumerate(h2_elements):
        title = _clean_text(h2.get_text())
        if not title or len(title) < 3:
            continue
        
        # Collect content between this H2 and the next H2 (or end)
        content_parts = []
        current = h2.next_sibling
        
        while current:
            if isinstance(current, Tag):
                # Stop at next H2
                if current.name == "h2":
                    break
                # Get text content from other elements
                text = current.get_text(strip=True)
                if text and len(text) > 10:
                    content_parts.append(text)
            current = current.next_sibling
        
        full_content = "\n\n".join(content_parts)
        
        # Skip if content too short
        if len(full_content) < MIN_CONTENT_LENGTH:
            continue
        
        # Determine category based on title and content
        category = _categorize_section(title, full_content)
        
        # Detect location for neighborhoods
        location = _detect_neighborhood(title)
        location_name = location[0] if location else None
        
        # Create section
        sections.append(ScrapedSection(
            title=location_name or title,
            title_hebrew=_clean_text(title),
            content=full_content,
            content_hebrew=_clean_text(full_content),
            category=category,
            subcategory=None,
            tags=_extract_tags(full_content),
            location_name=location_name,
        ))
    
    # Also extract individual restaurants from restaurant sections
    restaurant_sections = [s for s in sections if s.category == "restaurants"]
    for section in restaurant_sections:
        sub_restaurants = _extract_restaurants_from_section(section)
        sections.extend(sub_restaurants)
    
    # Also extract individual neighborhoods from neighborhood sections
    neighborhood_sections = [s for s in sections if s.category == "neighborhoods"]
    for section in neighborhood_sections:
        sub_neighborhoods = _extract_neighborhoods_from_section(section)
        sections.extend(sub_neighborhoods)
    
    logger.info("Parsed %d sections from blog", len(sections))
    return sections


def _categorize_section(title: str, content: str) -> str:
    """Categorize a section based on title and content."""
    title_lower = title.lower()
    combined = f"{title} {content[:500]}".lower()
    
    # Check title patterns first (most reliable)
    if any(kw in title for kw in ["רשימת הזהב", "המדריך לאכילה", "מסעדות", "לאכול"]):
        return "restaurants"
    if any(kw in title for kw in ["איפה לישון", "מלון", "לינה", "3/"]):
        return "hotels"
    if any(kw in title for kw in ["האיזורים", "שכונ", "4/"]):
        return "neighborhoods"
    if any(kw in title for kw in ["מה לקנות", "קניות", "8/"]):
        return "shopping"
    if any(kw in title for kw in ["קיוטו", "Kyoto", "10/"]):
        return "day_trips"
    if any(kw in title for kw in ["טיפים", "דגשים", "1/", "2/"]):
        return "practical_tips"
    if any(kw in title for kw in ["אטרקצי", "מקדש", "מוזיאון", "פארק"]):
        return "attractions"
    
    # Check content keywords
    if any(kw in combined for kw in ["ראמן", "סושי", "מסעדה", "לאכול", "אוכל", "יקיטורי"]):
        return "restaurants"
    if any(kw in combined for kw in ["מקדש", "פארק", "מוזיאון", "תצפית", "shrine", "temple"]):
        return "attractions"
    if any(kw in combined for kw in ["מלון", "לישון", "ריוקאן", "hostel", "hotel"]):
        return "hotels"
    
    # Check for neighborhood names
    if _detect_neighborhood(combined):
        return "neighborhoods"
    
    return "practical_tips"


def _extract_restaurants_from_section(section: ScrapedSection) -> list[ScrapedSection]:
    """Extract individual restaurants from a restaurant section."""
    restaurants = []
    content = section.content_hebrew
    
    # Look for restaurant names followed by descriptions
    for restaurant_name in GOLD_LIST_RESTAURANTS:
        if restaurant_name.lower() in content.lower():
            # Find the description around this restaurant
            idx = content.lower().find(restaurant_name.lower())
            if idx != -1:
                # Get context around the restaurant name (up to 500 chars after)
                start = max(0, idx - 20)
                end = min(len(content), idx + 500)
                context = content[start:end]
                
                # Find a natural break point
                break_points = [
                    context.find("\n\n", len(restaurant_name)),
                    context.find("–", len(restaurant_name) + 100),
                ]
                break_point = min(p for p in break_points if p > 0) if any(p > 0 for p in break_points) else 500
                description = context[:break_point].strip()
                
                if len(description) >= 80:
                    restaurants.append(ScrapedSection(
                        title=restaurant_name,
                        title_hebrew=restaurant_name,
                        content=description,
                        content_hebrew=description,
                        category="restaurants",
                        subcategory=section.title_hebrew,
                        tags=_extract_tags(description),
                        location_name=None,
                    ))
    
    return restaurants


def _extract_neighborhoods_from_section(section: ScrapedSection) -> list[ScrapedSection]:
    """Extract individual neighborhoods from a neighborhood section."""
    neighborhoods = []
    content = section.content_hebrew
    
    for key, (eng, heb) in NEIGHBORHOODS.items():
        # Check if this neighborhood is mentioned
        if eng.lower() in content.lower():
            idx = content.lower().find(eng.lower())
            if idx != -1:
                # Get context around the neighborhood
                start = max(0, idx)
                end = min(len(content), idx + 600)
                context = content[start:end]
                
                # Clean up
                description = context.strip()
                
                if len(description) >= 100:
                    neighborhoods.append(ScrapedSection(
                        title=eng,
                        title_hebrew=heb,
                        content=description,
                        content_hebrew=description,
                        category="neighborhoods",
                        subcategory=None,
                        tags=_extract_tags(description),
                        location_name=eng,
                    ))
    
    return neighborhoods


def scrape_blog() -> list[ScrapedSection]:
    """Main entry point: fetch and parse the blog."""
    html = fetch_blog_html()
    return parse_blog(html)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    logging.basicConfig(level=logging.INFO)
    results = scrape_blog()
    
    with open("scripts/scrape_results.txt", "w", encoding="utf-8") as f:
        by_cat = {}
        for section in results:
            by_cat.setdefault(section.category, []).append(section)
        
        for cat, items in sorted(by_cat.items()):
            f.write(f"\n{'='*60}\n")
            f.write(f"{cat.upper()} ({len(items)} items)\n")
            f.write(f"{'='*60}\n\n")
            
            for i, section in enumerate(items[:5]):  # First 5 per category
                f.write(f"[{i+1}] {section.title_hebrew}\n")
                f.write(f"    Location: {section.location_name}\n")
                f.write(f"    Tags: {section.tags}\n")
                f.write(f"    Content ({len(section.content_hebrew)} chars): {section.content_hebrew[:150]}...\n\n")
    
    print(f"Scraped {len(results)} sections - see scripts/scrape_results.txt")
    print("\nBy category:")
    by_cat = {}
    for s in results:
        by_cat.setdefault(s.category, []).append(s)
    for cat, items in sorted(by_cat.items()):
        print(f"  {cat}: {len(items)}")
