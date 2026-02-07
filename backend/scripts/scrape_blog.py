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

Each neighborhood (Shinjuku, Shibuya, etc.) has a bold header and
sub-sections for attractions.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from typing import Optional

import httpx
from bs4 import BeautifulSoup, NavigableString, Tag

logger = logging.getLogger(__name__)

BLOG_URL = "https://www.ptitim.com/tokyoguide/"

# Mapping from Hebrew section keywords to categories
SECTION_CATEGORY_MAP: dict[str, str] = {
    "דגשים": "practical_tips",
    "טיפים שימושיים": "practical_tips",
    "איפה לישון": "hotels",
    "האיזורים": "neighborhoods",
    "התחנות": "neighborhoods",
    "המפה הסודית": "practical_tips",
    "המדריך לאכילה": "restaurants",
    "רשימת הזהב": "restaurants",
    "מה לקנות": "shopping",
    "המשך קריאה": "practical_tips",
    "קיוטו": "day_trips",
}

# Known neighborhood names for category detection
NEIGHBORHOODS: list[str] = [
    "Shinjuku", "Harajuku", "Shibuya", "Ikebukuro", "Asakusa",
    "Ueno", "Ginza", "Tokyo Station", "Odaiba", "Akihabara",
    "Shimokitazawa", "Nakameguro", "Roppongi", "Jiyugaoka",
    "Yanaka", "Tsukiji", "Jimbocho", "Sugamo", "Suginami",
    "Shibamata", "Koenji", "Kichijoji",
    "שינג׳וקו", "הראג׳וקו", "שיבויה", "איקבוקורו", "אסקוסה",
    "אואנו", "גינזה", "אקיהאברה", "שימוקיטזאווה", "נקמגורו",
    "רופונגי",
]

# Restaurant names from the "Gold List"
GOLD_LIST_RESTAURANTS: list[str] = [
    "Nagi ramen", "Fu unji ramen", "Ginza Kagari", "Menya Hanabi",
    "butagumi", "Yamabe Okachimachi", "Gyukatsu Motomura", "Maguro Mart",
    "Tensuke", "Tsujihan", "shusai soba shodai", "Shinpachi Shokudo",
    "Miko Shokudo", "Coco Ichibanya", "Kitchen Nankai", "Uogashi Nihon-Ichi",
    "Kaiten Sushi Ginza Onodera", "Shouei Sushi Nakano", "Sushisho Masa",
    "Ebisu Endou", "Kosoan", "Lion cafe", "Sakurai souen", "Oiwake Dango",
    "Yoshinoya", "Shibuya morimoto", "Mentsu-dan", "Shin udon",
    "Kirimugiya Jinroku", "Menki Yashima Tomigaya", "Takamarusengyoten",
    "Hakushū Teppanyaki", "Harajuku Gyozaro", "Isomaru Suisan", "Marukou Suisan",
]


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


def _detect_category(title: str, content: str) -> str:
    """Detect the category based on title and content keywords."""
    combined = f"{title} {content[:200]}"

    # Check section category map
    for keyword, category in SECTION_CATEGORY_MAP.items():
        if keyword in combined:
            return category

    # Check for neighborhoods
    for neighborhood in NEIGHBORHOODS:
        if neighborhood.lower() in combined.lower():
            return "neighborhoods"

    # Check for restaurant names
    for restaurant in GOLD_LIST_RESTAURANTS:
        if restaurant.lower() in combined.lower():
            return "restaurants"

    # Check keywords
    if any(kw in combined for kw in ["מסעדה", "אוכל", "ראמן", "סושי", "איזקאיה", "יקיטורי"]):
        return "restaurants"
    if any(kw in combined for kw in ["מקדש", "מוזיאון", "פארק", "תצפית", "אטרקצי"]):
        return "attractions"
    if any(kw in combined for kw in ["מלון", "ריוקאן", "לינה", "לישון"]):
        return "hotels"
    if any(kw in combined for kw in ["רכבת", "מטרו", "מונית", "אוטובוס", "תחבורה", "IC card"]):
        return "transportation"
    if any(kw in combined for kw in ["קניות", "חנות", "לקנות", "דונקי", "מוג׳י"]):
        return "shopping"
    if any(kw in combined for kw in ["תה", "קימונו", "אונסן", "מסורת"]):
        return "cultural_experiences"
    if any(kw in combined for kw in ["קיוטו", "Kyoto"]):
        return "day_trips"

    return "practical_tips"


def _extract_tags(title: str, content: str) -> list[str]:
    """Extract relevant tags from the content."""
    tags = []
    combined = f"{title} {content}"

    tag_keywords = {
        "ראמן": "ramen",
        "סושי": "sushi",
        "טמפורה": "tempura",
        "אודון": "udon",
        "יקיטורי": "yakitori",
        "איזקאיה": "izakaya",
        "קארי": "curry",
        "מקדש": "temple",
        "פארק": "park",
        "מוזיאון": "museum",
        "שוק": "market",
        "קניות": "shopping",
        "קפה": "cafe",
        "בר": "bar",
        "וינטאג׳": "vintage",
        "אופנה": "fashion",
        "מנגה": "manga",
        "אנימה": "anime",
        "טבעוני": "vegan",
        "כשר": "kosher",
    }

    for hebrew, english in tag_keywords.items():
        if hebrew in combined:
            tags.append(english)

    return tags


def _detect_location_name(title: str, content: str) -> Optional[str]:
    """Try to extract the main English location name."""
    for neighborhood in NEIGHBORHOODS:
        if neighborhood in content or neighborhood in title:
            return neighborhood
    return None


def _clean_text(text: str) -> str:
    """Clean up extracted text: normalize whitespace, remove extra newlines."""
    # Normalize unicode spaces
    text = re.sub(r"\s+", " ", text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def fetch_blog_html() -> str:
    """Fetch the blog page HTML. Tries with browser headers, falls back to cached file."""
    logger.info("Fetching blog page: %s", BLOG_URL)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5,he;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    try:
        response = httpx.get(BLOG_URL, timeout=30, follow_redirects=True, headers=headers)
        response.raise_for_status()
        logger.info("Blog page fetched (%d bytes)", len(response.text))
        return response.text
    except Exception as e:
        logger.warning("Live fetch failed (%s), trying cached file...", e)
        # Fall back to locally cached HTML file
        cache_path = os.path.join(os.path.dirname(__file__), "blog_cache.html")
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                html = f.read()
            logger.info("Using cached blog content (%d bytes)", len(html))
            return html
        raise RuntimeError(f"Cannot fetch blog and no cache file at {cache_path}")


def parse_blog(html: str) -> list[ScrapedSection]:
    """
    Parse the blog HTML into structured sections.

    The blog uses a combination of H1, H2, H3, bold text, and paragraphs.
    We split on major headers and bold sub-headers to create individual content items.
    """
    soup = BeautifulSoup(html, "lxml")

    # Find the main content area - try multiple selectors
    content_area = soup.find("div", class_="post__content")
    if not content_area:
        content_area = soup.find("div", class_="entry-content")
    if not content_area:
        # Fallback: try article body
        content_area = soup.find("article")
    if not content_area:
        logger.warning("Could not find main content area, using body")
        content_area = soup.find("body")

    if content_area is None:
        logger.error("Could not parse blog HTML")
        return []

    sections: list[ScrapedSection] = []
    current_title = ""
    current_content_parts: list[str] = []
    current_major_section = ""

    # Walk through all direct children and nested elements
    elements = content_area.find_all(["h1", "h2", "h3", "p", "ul", "ol", "blockquote"])

    for element in elements:
        tag_name = element.name
        text = element.get_text(strip=True)

        if not text:
            continue

        # Major section headers (H1, H2, H3)
        if tag_name in ("h1", "h2", "h3"):
            # Save the previous section if it has content
            if current_title and current_content_parts:
                full_content = "\n".join(current_content_parts)
                if len(full_content) > 50:  # Skip very short sections
                    category = _detect_category(current_title, full_content)
                    sections.append(
                        ScrapedSection(
                            title=_detect_location_name(current_title, full_content) or current_title,
                            title_hebrew=_clean_text(current_title),
                            content=full_content,
                            content_hebrew=_clean_text(full_content),
                            category=category,
                            subcategory=current_major_section if current_major_section != current_title else None,
                            tags=_extract_tags(current_title, full_content),
                            location_name=_detect_location_name(current_title, full_content),
                        )
                    )

            current_title = text
            current_content_parts = []

            # Track major section for subcategory
            if tag_name in ("h1", "h2"):
                current_major_section = text

        # Bold text that looks like a sub-header (neighborhood names, restaurant names)
        elif tag_name == "p" and element.find("strong"):
            strong = element.find("strong")
            strong_text = strong.get_text(strip=True) if strong else ""

            # Check if this bold text is a sub-section header (like a neighborhood or attraction)
            is_header = (
                len(strong_text) > 3
                and len(strong_text) < 100
                and (
                    any(n.lower() in strong_text.lower() for n in NEIGHBORHOODS)
                    or any(r.lower() in strong_text.lower() for r in GOLD_LIST_RESTAURANTS)
                    or strong_text.startswith("אטרקציות")
                )
            )

            if is_header and current_content_parts:
                # Save current section and start a new sub-section
                full_content = "\n".join(current_content_parts)
                if len(full_content) > 50:
                    category = _detect_category(current_title, full_content)
                    sections.append(
                        ScrapedSection(
                            title=_detect_location_name(current_title, full_content) or current_title,
                            title_hebrew=_clean_text(current_title),
                            content=full_content,
                            content_hebrew=_clean_text(full_content),
                            category=category,
                            subcategory=current_major_section if current_major_section != current_title else None,
                            tags=_extract_tags(current_title, full_content),
                            location_name=_detect_location_name(current_title, full_content),
                        )
                    )
                current_title = strong_text
                current_content_parts = [text]
            else:
                current_content_parts.append(text)
        else:
            current_content_parts.append(text)

    # Don't forget the last section
    if current_title and current_content_parts:
        full_content = "\n".join(current_content_parts)
        if len(full_content) > 50:
            category = _detect_category(current_title, full_content)
            sections.append(
                ScrapedSection(
                    title=_detect_location_name(current_title, full_content) or current_title,
                    title_hebrew=_clean_text(current_title),
                    content=full_content,
                    content_hebrew=_clean_text(full_content),
                    category=category,
                    subcategory=current_major_section if current_major_section != current_title else None,
                    tags=_extract_tags(current_title, full_content),
                    location_name=_detect_location_name(current_title, full_content),
                )
            )

    logger.info("Parsed %d sections from blog", len(sections))
    return sections


def scrape_blog() -> list[ScrapedSection]:
    """Main entry point: fetch and parse the blog."""
    html = fetch_blog_html()
    return parse_blog(html)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    logging.basicConfig(level=logging.INFO)
    results = scrape_blog()
    
    # Write results to file to avoid encoding issues
    with open("scripts/scrape_results.txt", "w", encoding="utf-8") as f:
        for i, section in enumerate(results):
            f.write(f"\n[{i+1}] ({section.category}) {section.title_hebrew}\n")
            f.write(f"    Location: {section.location_name}\n")
            f.write(f"    Tags: {section.tags}\n")
            f.write(f"    Content: {section.content_hebrew[:120]}...\n")
    
    print(f"Scraped {len(results)} sections - see scripts/scrape_results.txt")
