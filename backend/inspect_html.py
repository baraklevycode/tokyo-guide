"""Inspect blog HTML structure to fix the parser."""
from bs4 import BeautifulSoup

with open("scripts/blog_cache.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

with open("html_structure.txt", "w", encoding="utf-8") as out:
    article = soup.find("article")
    out.write(f"ARTICLE: {'found' if article else 'not found'}\n")
    if article:
        out.write(f"  class: {article.get('class')}\n")

    for cls in ["entry-content", "post-content", "article-content", "theiaPostSlider_pre498"]:
        elem = soup.find("div", class_=cls)
        out.write(f"div.{cls}: {'found' if elem else 'not found'}\n")

    for tag in ["h1", "h2", "h3"]:
        headers = soup.find_all(tag)
        out.write(f"\n{tag}: {len(headers)} found\n")
        for h in headers[:8]:
            out.write(f"  [{h.get_text(strip=True)[:100]}]\n")

    # Show first 3 bold elements to understand structure
    strongs = soup.find_all("strong")
    out.write(f"\nstrong tags: {len(strongs)} total\n")
    for s in strongs[:10]:
        out.write(f"  [{s.get_text(strip=True)[:80]}]\n")

    # Check paragraphs count
    paras = soup.find_all("p")
    out.write(f"\np tags: {len(paras)} total\n")

    main_tag = soup.find("main")
    out.write(f"main: {'found' if main_tag else 'not found'}\n")

    # Show body > direct children tag names
    body = soup.find("body")
    if body:
        children = [c.name for c in body.children if c.name]
        out.write(f"body direct children: {children[:20]}\n")
