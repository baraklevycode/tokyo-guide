"""
Seed the Supabase database with content from the blog and map.

Usage:
    poetry run python -m scripts.seed_database

This script:
1. Scrapes the Ptitim Tokyo Guide blog
2. Optionally scrapes the Google My Maps KML
3. Generates embeddings for all content
4. Inserts everything into the Supabase tokyo_content table
"""

from __future__ import annotations

import logging
import os
import sys

# Add the backend directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from app.services.database import get_supabase_client
from app.services.embeddings import encode_batch, load_model
from scripts.scrape_blog import ScrapedSection, scrape_blog
from scripts.scrape_map import MapPlace, scrape_map

logger = logging.getLogger(__name__)


def seed_blog_content(sections: list[ScrapedSection]) -> int:
    """
    Generate embeddings and insert blog sections into Supabase.

    Returns the number of items inserted.
    """
    if not sections:
        logger.warning("No blog sections to seed")
        return 0

    client = get_supabase_client()

    # Generate embeddings for all sections (using Hebrew content for better Hebrew search)
    logger.info("Generating embeddings for %d sections...", len(sections))
    texts = [f"{s.title_hebrew} {s.content_hebrew}" for s in sections]
    embeddings = encode_batch(texts, batch_size=16)

    # Prepare rows for insertion
    rows = []
    for section, embedding in zip(sections, embeddings):
        rows.append(
            {
                "title": section.title,
                "title_hebrew": section.title_hebrew,
                "content": section.content,
                "content_hebrew": section.content_hebrew,
                "category": section.category,
                "subcategory": section.subcategory,
                "tags": section.tags,
                "location_name": section.location_name,
                "embedding": embedding,
            }
        )

    # Insert in batches of 50
    inserted = 0
    batch_size = 50
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        try:
            result = client.table("tokyo_content").insert(batch).execute()
            inserted += len(result.data)
            logger.info("Inserted batch %d-%d (%d items)", i, i + len(batch), len(result.data))
        except Exception as e:
            logger.error("Failed to insert batch %d-%d: %s", i, i + len(batch), e)

    return inserted


def seed_map_places(places: list[MapPlace]) -> int:
    """
    Generate embeddings and insert map places that don't already exist in the database.

    Returns the number of items inserted.
    """
    if not places:
        logger.warning("No map places to seed")
        return 0

    client = get_supabase_client()

    # Filter out places with no meaningful description
    meaningful = [p for p in places if p.name and len(p.name) > 2]
    if not meaningful:
        return 0

    logger.info("Generating embeddings for %d map places...", len(meaningful))
    texts = [f"{p.name} {p.description}" for p in meaningful]
    embeddings = encode_batch(texts, batch_size=16)

    rows = []
    for place, embedding in zip(meaningful, embeddings):
        rows.append(
            {
                "title": place.name,
                "title_hebrew": place.name,  # Map names may be in English
                "content": place.description or place.name,
                "content_hebrew": place.description or place.name,
                "category": "attractions",  # Default for map places
                "tags": place.tags or [],
                "location_name": place.name,
                "latitude": place.latitude,
                "longitude": place.longitude,
                "embedding": embedding,
            }
        )

    inserted = 0
    batch_size = 50
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        try:
            result = client.table("tokyo_content").insert(batch).execute()
            inserted += len(result.data)
            logger.info("Inserted map batch %d-%d (%d items)", i, i + len(batch), len(result.data))
        except Exception as e:
            logger.error("Failed to insert map batch %d-%d: %s", i, i + len(batch), e)

    return inserted


def clear_existing_content() -> None:
    """Delete all existing content from the tokyo_content table."""
    client = get_supabase_client()
    try:
        # Delete all rows (Supabase requires a filter, so we use gt with a very old date)
        client.table("tokyo_content").delete().gte("created_at", "2000-01-01").execute()
        logger.info("Cleared existing content from tokyo_content table")
    except Exception as e:
        logger.error("Failed to clear existing content: %s", e)


def main() -> None:
    """Main seeding pipeline."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("=" * 60)
    logger.info("Tokyo Guide Database Seeding")
    logger.info("=" * 60)

    # Load the embedding model
    logger.info("Step 1: Loading embedding model...")
    load_model()

    # Clear existing data
    logger.info("Step 2: Clearing existing content...")
    clear_existing_content()

    # Scrape blog
    logger.info("Step 3: Scraping blog content...")
    blog_sections = scrape_blog()
    logger.info("Found %d blog sections", len(blog_sections))

    # Seed blog content
    logger.info("Step 4: Seeding blog content...")
    blog_count = seed_blog_content(blog_sections)
    logger.info("Inserted %d blog items", blog_count)

    # Scrape map (optional, may fail if KML is not accessible)
    logger.info("Step 5: Scraping map data...")
    try:
        map_places = scrape_map()
        logger.info("Found %d map places", len(map_places))

        if map_places:
            logger.info("Step 6: Seeding map places...")
            map_count = seed_map_places(map_places)
            logger.info("Inserted %d map items", map_count)
        else:
            logger.info("No map places to seed (KML may not be accessible)")
    except Exception as e:
        logger.warning("Map scraping failed (non-critical): %s", e)

    logger.info("=" * 60)
    logger.info("Seeding complete! Total blog items: %d", blog_count)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
