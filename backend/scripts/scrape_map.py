"""
Scraper for the Google My Maps "Tokyo by Ptitim" map.

Attempts to export the KML data from the public map and extract place names,
coordinates, and descriptions.

Map ID: 1I0o12hoecmBorcEsinQqw4nhTDG7adU
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# KML export URL for the Google My Maps
KML_URL = "https://www.google.com/maps/d/kml?mid=1I0o12hoecmBorcEsinQqw4nhTDG7adU&forcekml=1"


@dataclass
class MapPlace:
    """A place extracted from the Google My Maps KML."""

    name: str
    description: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    layer_name: str = ""
    tags: list[str] = field(default_factory=list)


def fetch_kml() -> str:
    """Fetch the KML data from Google My Maps."""
    logger.info("Fetching KML from: %s", KML_URL)
    try:
        response = httpx.get(KML_URL, timeout=30, follow_redirects=True)
        response.raise_for_status()
        logger.info("KML fetched (%d bytes)", len(response.text))
        return response.text
    except Exception as e:
        logger.warning("Could not fetch KML data: %s", e)
        return ""


def parse_kml(kml_content: str) -> list[MapPlace]:
    """Parse KML XML and extract places with coordinates."""
    if not kml_content:
        return []

    soup = BeautifulSoup(kml_content, "lxml-xml")
    places: list[MapPlace] = []

    # Find all Folder elements (layers in Google My Maps)
    folders = soup.find_all("Folder")

    for folder in folders:
        folder_name_elem = folder.find("name", recursive=False)
        layer_name = folder_name_elem.get_text(strip=True) if folder_name_elem else ""

        # Find all Placemark elements within this folder
        placemarks = folder.find_all("Placemark")

        for placemark in placemarks:
            name_elem = placemark.find("name")
            name = name_elem.get_text(strip=True) if name_elem else ""

            # Get description (may contain HTML)
            desc_elem = placemark.find("description")
            description = ""
            if desc_elem:
                raw_desc = desc_elem.get_text(strip=True)
                # Clean HTML entities
                desc_soup = BeautifulSoup(raw_desc, "html.parser")
                description = desc_soup.get_text(strip=True)

            # Get coordinates
            coord_elem = placemark.find("coordinates")
            lat: Optional[float] = None
            lng: Optional[float] = None
            if coord_elem:
                coord_text = coord_elem.get_text(strip=True)
                # KML format: longitude,latitude,altitude
                parts = coord_text.split(",")
                if len(parts) >= 2:
                    try:
                        lng = float(parts[0])
                        lat = float(parts[1])
                    except ValueError:
                        pass

            if name:
                places.append(
                    MapPlace(
                        name=name,
                        description=description,
                        latitude=lat,
                        longitude=lng,
                        layer_name=layer_name,
                    )
                )

    logger.info("Parsed %d places from KML", len(places))
    return places


def _categorize_layer(layer_name: str) -> str:
    """Map KML layer name to a content category."""
    layer_lower = layer_name.lower()
    if any(kw in layer_lower for kw in ["food", "restaurant", "eat", "אוכל", "מסעד"]):
        return "restaurants"
    if any(kw in layer_lower for kw in ["shop", "buy", "קניות"]):
        return "shopping"
    if any(kw in layer_lower for kw in ["hotel", "sleep", "מלון", "לינה"]):
        return "hotels"
    if any(kw in layer_lower for kw in ["cafe", "coffee", "קפה"]):
        return "restaurants"
    if any(kw in layer_lower for kw in ["bar", "drink", "בר"]):
        return "restaurants"
    if any(kw in layer_lower for kw in ["sight", "attraction", "temple", "אטרקצ"]):
        return "attractions"
    return "attractions"


def scrape_map() -> list[MapPlace]:
    """Main entry point: fetch and parse the Google My Maps KML."""
    kml = fetch_kml()
    return parse_kml(kml)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    places = scrape_map()
    for i, place in enumerate(places):
        print(f"[{i+1}] {place.name}")
        print(f"    Layer: {place.layer_name}")
        print(f"    Coords: {place.latitude}, {place.longitude}")
        print(f"    Desc: {place.description[:100]}..." if place.description else "    Desc: (none)")
