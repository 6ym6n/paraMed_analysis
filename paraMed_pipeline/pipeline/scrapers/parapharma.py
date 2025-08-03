"""
Scraper for parapharma.ma.

This module defines functions to fetch product listings from the
parapharma e‑commerce site.  Each category is paginated; the scraper
iterates over pages until no products are found or an optional
``max_pages`` limit is reached.  The returned product dictionaries use
a consistent schema ready for further cleaning and merging.
"""

from __future__ import annotations

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Iterable, Optional

from ..utils.cleaning import clean_price

DEFAULT_SITE = "parapharma.ma"


def scrape_category_page(category_url: str, category_name: str, *, max_pages: Optional[int] = None) -> List[Dict]:
    """Scrape all products from a single category page.

    Parameters
    ----------
    category_url : str
        Base URL of the category to scrape (without pagination query).
    category_name : str
        Human‑readable category name.  Stored in each product under the
        ``"category"`` key.
    max_pages : int, optional
        Maximum number of pages to scrape.  If ``None``, scrape until
        there are no more products.

    Returns
    -------
    list of dict
        A list of product dictionaries.  Each dictionary contains
        ``site``, ``category``, ``name``, ``price``, ``discount``,
        ``original_price``, ``is_discounted``, ``availability``,
        ``product_url``, ``image_url`` and ``scraped_at`` fields.
    """
    results: List[Dict] = []
    page = 1
    while True:
        # Stop if we've reached the maximum page limit
        if max_pages is not None and page > max_pages:
            break
        url = f"{category_url}?page={page}"
        print(f"📦 [parapharma] Scraping {category_name} page {page}: {url}")
        try:
            resp = requests.get(url, timeout=30)
        except Exception as e:
            print(f"⚠️ Request failed: {e}")
            break
        if resp.status_code != 200:
            print(f"⚠️ HTTP {resp.status_code} for {url}")
            break
        soup = BeautifulSoup(resp.text, "html.parser")
        product_cards = soup.select(".product-miniature")
        if not product_cards:
            # No products found: end of pagination
            break
        for card in product_cards:
            try:
                name_el = card.select_one("h2.h3.product-title")
                name = name_el.get_text(strip=True) if name_el else ""
                # Price (discounted or not)
                price_el = card.select_one("span.price")
                price = clean_price(price_el.get_text(strip=True)) if price_el else None
                # Discount (if present)
                discount_el = card.select_one("span.discount-amount.discount-product")
                discount = None
                original_price = price
                is_discounted = False
                if discount_el:
                    disc_value = clean_price(discount_el.get_text(strip=True))
                    if disc_value is not None and price is not None:
                        discount = disc_value
                        original_price = round(price + discount, 2)
                        is_discounted = True
                # Availability
                out_of_stock = card.select_one("li.product-flag.out_of_stock") is not None
                availability = "rupture" if out_of_stock else "disponible"
                # Product URL
                link_el = card.select_one("a")
                product_url = None
                if link_el and link_el.has_attr("href"):
                    href = link_el["href"]
                    product_url = href if href.startswith("http") else f"https://{DEFAULT_SITE}{href}"
                # Image URL
                img_el = card.select_one("img.img-fluid")
                image_url = img_el["src"] if img_el and img_el.has_attr("src") else None
                results.append({
                    "site": DEFAULT_SITE,
                    "category": category_name,
                    "name": name,
                    "price": price,
                    "discount": discount,
                    "original_price": original_price,
                    "is_discounted": is_discounted,
                    "availability": availability,
                    "product_url": product_url,
                    "image_url": image_url,
                    "scraped_at": datetime.utcnow().isoformat(),
                })
            except Exception as e:
                print(f"⚠️ Error parsing product: {e}")
        page += 1
    return results


def scrape_all(categories: Iterable[Dict], *, max_pages: Optional[int] = None) -> List[Dict]:
    """Scrape products from all categories.

    Parameters
    ----------
    categories : iterable of dict
        An iterable of category dictionaries with ``"name"`` and ``"url"`` keys.
    max_pages : int, optional
        Maximum number of pages per category.

    Returns
    -------
    list of dict
        Consolidated list of product dictionaries from all categories.
    """
    all_products: List[Dict] = []
    for cat in categories:
        name = cat.get("name") or ""
        url = cat.get("url") or ""
        if not url:
            continue
        products = scrape_category_page(url, name, max_pages=max_pages)
        all_products.extend(products)
    return all_products


__all__ = ["scrape_category_page", "scrape_all"]