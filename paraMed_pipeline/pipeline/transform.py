"""
Data transformation and merging.

This module provides a function to merge raw product dictionaries from
multiple sources and normalise them into a unified schema suitable for
matching.  It applies cleaning, brand extraction, size extraction,
price/discount logic, availability normalisation and category mapping.

The function can deduplicate entries based on site and cleaned name.
"""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Dict, Tuple, Optional, Set

from .utils.cleaning import (
    clean_name,
    extract_brand,
    extract_size,
    normalize_availability,
    map_category,
)

def _parse_datetime(value: Optional[str]) -> datetime:
    """Parse an ISO datetime string into a datetime.  Fallback to now."""
    if value:
        try:
            return datetime.fromisoformat(value)
        except Exception:
            pass
    return datetime.utcnow()


def merge_and_clean(
    parapharma_docs: Iterable[Dict],
    univers_docs: Iterable[Dict],
    *,
    deduplicate: bool = True,
) -> List[Dict]:
    """Merge and normalise product documents from Parapharma and Univers.

    Parameters
    ----------
    parapharma_docs : iterable of dict
        Raw documents scraped from parapharma.ma.
    univers_docs : iterable of dict
        Raw documents scraped from universparadiscount.ma.
    deduplicate : bool, optional
        If ``True``, remove duplicates within each site based on
        ``clean_name``.  Only the first occurrence is kept.

    Returns
    -------
    list of dict
        Cleaned documents with unified fields: ``site``, ``product_url``,
        ``category``, ``main_category``, ``name``, ``clean_name``,
        ``brand``, ``size``, ``price``, ``original_price``, ``discount``,
        ``is_discounted``, ``availability``, ``image_url`` and
        ``scraped_at`` (as datetime).
    """
    cleaned: List[Dict] = []
    seen_keys: Set[Tuple[str, str]] = set()

    def process(doc: Dict) -> Optional[Dict]:
        site: str = doc.get("site", "").strip().lower()
        name_raw: str = doc.get("name", "")
        clean = clean_name(name_raw)
        if deduplicate:
            key = (site, clean)
            if key in seen_keys:
                return None
            seen_keys.add(key)
        product_url = doc.get("product_url") or doc.get("url") or None
        category = (doc.get("category") or "").strip().lower()
        main_category = map_category(category)
        # Prices
        price = doc.get("price")
        original_price = doc.get("original_price")
        # Determine discount and flag
        discount = None
        is_discounted = False
        if original_price is not None and price is not None:
            disc = original_price - price
            if disc > 0:
                discount = round(disc, 2)
                is_discounted = True
        # Availability
        raw_avail = doc.get("availability")
        if raw_avail is None and doc.get("is_out_of_stock") is not None:
            raw_avail = "out_of_stock" if doc.get("is_out_of_stock") else "in_stock"
        availability = normalize_availability(raw_avail)
        image_url = doc.get("image_url")
        scraped_at_str = doc.get("scraped_at")
        scraped_at = _parse_datetime(scraped_at_str)
        brand = extract_brand(clean)
        size = extract_size(clean)
        return {
            "site": site,
            "product_url": product_url,
            "category": category,
            "main_category": main_category,
            "name": name_raw,
            "clean_name": clean,
            "brand": brand,
            "size": size,
            "price": price,
            "original_price": original_price,
            "discount": discount,
            "is_discounted": is_discounted,
            "availability": availability,
            "image_url": image_url,
            "scraped_at": scraped_at,
        }

    for doc in parapharma_docs:
        item = process(doc)
        if item:
            cleaned.append(item)
    for doc in univers_docs:
        item = process(doc)
        if item:
            cleaned.append(item)
    return cleaned


__all__ = ["merge_and_clean"]