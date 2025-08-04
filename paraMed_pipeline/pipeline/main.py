"""
Pipeline orchestrator.

This module provides a high‑level function to run the entire data
pipeline: scraping both e‑commerce sites, merging and cleaning the
results, storing them in MongoDB and performing product matching.  It
serves as a single entry point for routine data refreshes.

Run this module as a script to execute the full pipeline::

    python -m paraMed_pipeline.pipeline.main

Make sure your environment variables for MongoDB are configured (see
``utils/db.py``) before running.
"""

from __future__ import annotations

from typing import Optional, List, Dict

from .scrapers.parapharma import scrape_all as scrape_parapharma
from .scrapers.univers import scrape_all as scrape_univers
from ..config import PARAPHARMA_CATEGORIES, UNIVERS_CATEGORIES
from .transform import merge_and_clean
from .matcher import match_products
from .utils.db import get_collection


def run_pipeline(
    *,
    max_pages_parapharma: Optional[int] = 156,
    max_pages_univers: Optional[int] = 1
) -> None:
    """Execute the full scraping, transformation and matching pipeline.

    Parameters
    ----------
    max_pages_parapharma : int, optional
        Page limit for Parapharma scraper.
    max_pages_univers : int, optional
        Page limit for Univers scraper.
    """
    print("🚀 Starting scraping...")
    # Step 1: scrape raw data
    parapharma_raw = scrape_parapharma(PARAPHARMA_CATEGORIES, max_pages=max_pages_parapharma)
    univers_raw = scrape_univers(UNIVERS_CATEGORIES, max_pages=max_pages_univers)
    print(f"✅ Scraped {len(parapharma_raw)} Parapharma products and {len(univers_raw)} Univers products")
    # Step 2: clean and merge
    print("🧹 Cleaning and merging data...")
    cleaned = merge_and_clean(parapharma_raw, univers_raw)
    print(f"✅ Produced {len(cleaned)} cleaned products")
    # Persist cleaned data
    merged_col = get_collection("para_univer_merged")
    if cleaned:
        merged_col.delete_many({})
        merged_col.insert_many(cleaned)
        print(f"💾 Saved cleaned products to para_univer_merged")
    else:
        print("⚠️ No cleaned products to save")
    # Step 3: matching
    print("⚖️ Matching products...")
    parapharma_clean = [d for d in cleaned if d.get("site") == "parapharma.ma"]
    univers_clean = [d for d in cleaned if d.get("site") == "universparadiscount.ma"]
    matches = match_products(parapharma_clean, univers_clean)
    print(f"✅ Found {len(matches)} matches")
    matches_col = get_collection("matches")
    if matches:
        matches_col.delete_many({})
        matches_col.insert_many(matches)
        print(f"💾 Saved matches to matches collection")
    else:
        print("⚠️ No matches found to save")

if __name__ == "__main__":
    run_pipeline()
