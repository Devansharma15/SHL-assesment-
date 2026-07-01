"""SHL catalog scraper using Playwright for JavaScript-rendered pages.

This is a supplementary tool for enriching the curated catalog.
The primary data source is the hand-curated catalog.json file.

Usage:
    python -m scraper.shl_scraper
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CATALOG_PATH = DATA_DIR / "shl_product_catalog.json"

SHL_CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"


def scrape_catalog() -> list[dict]:
    """Scrape the SHL product catalog using Playwright.

    Returns:
        List of assessment dicts scraped from the catalog page.

    Note:
        This requires playwright and its browser binaries to be installed:
        pip install playwright && playwright install chromium
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error(
            "Playwright not installed. Install with: pip install playwright && playwright install chromium"
        )
        return []

    assessments = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        logger.info("Navigating to SHL catalog: %s", SHL_CATALOG_URL)
        page.goto(SHL_CATALOG_URL, wait_until="networkidle")
        page.wait_for_timeout(3000)  # Wait for JavaScript rendering

        # Try to find assessment cards/links on the page
        # SHL's catalog page structure may vary — this is best-effort
        links = page.query_selector_all("a[href*='product-catalog']")

        for link in links:
            try:
                name = link.inner_text().strip()
                href = link.get_attribute("href")
                if name and href and len(name) > 3:
                    full_url = href if href.startswith("http") else f"https://www.shl.com{href}"
                    assessments.append(
                        {
                            "name": name,
                            "url": full_url,
                            "scraped": True,
                        }
                    )
            except Exception as e:
                logger.debug("Error extracting link: %s", e)

        logger.info("Scraped %d assessment links from catalog page.", len(assessments))
        browser.close()

    return assessments


def merge_with_existing(
    scraped: list[dict],
    existing_path: Path | None = None,
) -> list[dict]:
    """Merge scraped data with the existing curated catalog.

    Only adds new assessments not already in the curated catalog.

    Args:
        scraped: List of scraped assessment dicts.
        existing_path: Path to existing catalog.json.

    Returns:
        Merged catalog list.
    """
    path = existing_path or CATALOG_PATH

    if path.exists():
        with open(path, encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = []

    existing_urls = {a.get("url", "").rstrip("/") for a in existing}

    new_count = 0
    for assessment in scraped:
        url = assessment.get("url", "").rstrip("/")
        if url and url not in existing_urls:
            existing.append(assessment)
            existing_urls.add(url)
            new_count += 1

    logger.info("Merged %d new assessments into catalog.", new_count)
    return existing


def main():
    """CLI entry point for the scraper."""
    logging.basicConfig(level=logging.INFO)

    logger.info("Starting SHL catalog scrape...")
    scraped = scrape_catalog()

    if scraped:
        merged = merge_with_existing(scraped)

        # Save
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        output_path = DATA_DIR / "catalog_scraped.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)

        logger.info("Scraped catalog saved to: %s", output_path)
    else:
        logger.warning("No assessments scraped. Using curated catalog only.")


if __name__ == "__main__":
    main()
