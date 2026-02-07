"""
Fetch the blog content via httpx with a full browser TLS fingerprint,
save it to a cache file, then run the seeding pipeline.
"""
import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()

import httpx

BLOG_URL = "https://www.ptitim.com/tokyoguide/"
CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blog_cache.html")


def fetch_with_full_headers() -> str:
    """Fetch using httpx with full browser impersonation."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,he;q=0.8",
        # Note: Omit Accept-Encoding to get uncompressed response
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": '"Chromium";v="131", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }

    with httpx.Client(http2=True, follow_redirects=True, timeout=60) as client:
        resp = client.get(BLOG_URL, headers=headers)
        resp.raise_for_status()
        return resp.text


def main():
    # Try to fetch the blog
    logger.info("Fetching blog content...")
    try:
        html = fetch_with_full_headers()
        logger.info("Blog fetched successfully (%d bytes)", len(html))
    except Exception as e:
        logger.warning("HTTP fetch failed: %s", e)
        # Check if cache already exists
        if os.path.exists(CACHE_PATH):
            logger.info("Using existing cache file")
        else:
            logger.error("No cache file available. Cannot proceed.")
            sys.exit(1)
        html = None

    if html:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info("Saved blog HTML to cache: %s", CACHE_PATH)

    # Now run the seeding pipeline
    logger.info("Starting database seeding...")
    from scripts.seed_database import main as seed_main
    seed_main()


if __name__ == "__main__":
    main()
