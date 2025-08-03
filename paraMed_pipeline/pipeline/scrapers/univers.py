"""
Scraper for universparadiscount.ma.

This module defines functions to fetch product listings from the
Univers ParaDiscount site.  Similar to the parapharma scraper, it
iterates over category pages until no products are found or an optional
``max_pages`` limit is reached.  The returned product dictionaries
follow a consistent schema for further processing.
"""

from __future__ import annotations

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Iterable, Optional

from ..utils.cleaning import clean_price

DEFAULT_SITE = "universparadiscount.ma"


def scrape_category_page(category_url: str, category_name: str, *, max_pages: Optional[int] = None) -> List[Dict]:
    """Scrape all products from a single category of the Univers site.

    Parameters
    ----------
    category_url : str
        Base URL of the category (without pagination query).
    category_name : str
        Name of the category.  Added to each product under the ``"category"`` key.
    max_pages : int, optional
        Maximum number of pages to scrape.  ``None`` means scrape until
        no products are found.

    Returns
    -------
    list of dict
        A list of product dictionaries, each containing ``site``,
        ``category``, ``name``, ``price``, ``discount``,
        ``original_price``, ``is_discounted``, ``availability``,
        ``product_url``, ``image_url`` and ``scraped_at``.
    """
    results: List[Dict] = []
    page = 1
    while True:
        if max_pages is not None and page > max_pages:
            break
        url = f"{category_url}?resultsPerPage=3846&page={page}"
        print(f"📦 [univers] Scraping {category_name} page {page}: {url}")
        try:
            resp = requests.get(url, timeout=30)
        except Exception as e:
            print(f"⚠️ Request failed: {e}")
            break
        if resp.status_code != 200:
            print(f"⚠️ HTTP {resp.status_code} for {url}")
            break
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select("div.item")
        if not items:
            break
        for item in items:
            try:
                # Name and URL
                name = None
                name_tag = item.select_one(".product_name a")
                if name_tag:
                    name = name_tag.get("title") or name_tag.get_text(strip=True)
                product_url = None
                if name_tag and name_tag.has_attr("href"):
                    href = name_tag["href"]
                    product_url = href if href.startswith("http") else f"https://{DEFAULT_SITE}{href}"
                # Image
                image_url = None
                img_tag = item.select_one("img.ax-img-loader")
                if img_tag and img_tag.has_attr("src"):
                    image_url = img_tag["src"]
                # Category (fallback to provided category_name)
                category_tag = item.select_one(".ax-product-cats a")
                category = category_tag.get_text(strip=True) if category_tag else category_name
                # Prices
                original_price = None
                discounted_price = None
                orig_tag = item.select_one("span.regular-price")
                if orig_tag:
                    original_price = clean_price(orig_tag.get_text())
                disc_tag = item.select_one("span.price")
                if disc_tag:
                    discounted_price = clean_price(disc_tag.get_text())
                # Determine price, discount and flag
                price = None
                discount = None
                is_discounted = False
                # If both present and discount price is lower, use discounted
                if discounted_price is not None and original_price is not None and discounted_price < original_price:
                    price = discounted_price
                    discount = round(original_price - discounted_price, 2)
                    is_discounted = True
                else:
                    price = discounted_price or original_price
                    if original_price is not None and price is not None and original_price > price:
                        discount = round(original_price - price, 2)
                        is_discounted = True
                # Flags
                flags = item.select(".label-flag")
                out_of_stock = any("type-out_of_stock" in f.get("class", []) for f in flags)
                availability = "rupture" if out_of_stock else "disponible"
                results.append({
                    "site": DEFAULT_SITE,
                    "category": category,
                    "name": name or "",
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
                print(f"⚠️ Error parsing univers product: {e}")
        page += 1
    return results


def scrape_all(categories: Iterable[Dict], *, max_pages: Optional[int] = None) -> List[Dict]:
    """Scrape products from all Univers categories.

    Parameters
    ----------
    categories : iterable of dict
        A sequence of categories with ``"name"`` and ``"url"`` fields.
    max_pages : int, optional
        Maximum number of pages per category.

    Returns
    -------
    list of dict
        Combined list of products from all categories.
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