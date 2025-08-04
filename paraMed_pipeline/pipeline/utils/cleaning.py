"""
Text and value normalisation utilities.

This module contains helper functions to normalise product names,
extract brands and sizes, clean prices and availability labels, and
map categories.  By using these functions in both the scraping and
transformation stages you ensure consistent preprocessing throughout
the pipeline.

The implementation here is based on the upstream repository.  In
addition to the original helpers, this version also exposes a helper
to recover truncated product names from Parapharma image URLs.  Some
Parapharma product listings abbreviate long names with an ellipsis
(`"..."`).  When this occurs the full name can often be inferred
from the associated image URL, which encodes a slugified version of
the product name.  The ``clean_name_from_image_url`` function
extracts the slug from the URL, converts hyphens to spaces and
returns a title‑cased version.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from typing import Optional, Tuple

# Note: these imports reference project configuration.  They may be
# unavailable when this stub is used in isolation, but are required in
# the full pipeline.  Comment them out if running this file alone.
try:
    from .category_mapping import category_mapping  # type: ignore
    from ..config import KNOWN_BRANDS, BRAND_BLACKLIST  # type: ignore
except Exception:
    category_mapping = {}
    KNOWN_BRANDS: Tuple[str, ...] = tuple()
    BRAND_BLACKLIST: Tuple[str, ...] = tuple()

__all__ = [
    "clean_name",
    "extract_size",
    "extract_brand",
    "normalize_availability",
    "clean_price",
    "map_category",
    "clean_name_from_image_url",
]


def _strip_accents(text: str) -> str:
    """Remove accents from a unicode string."""
    return unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")


def clean_name(name: Optional[str]) -> str:
    """Normalise a product name.

    This function lowercases the name, removes accents, replaces
    hyphens/underscores with spaces, strips non‑alphanumeric characters
    and collapses whitespaces.  It also concatenates numbers and units
    (e.g. ``"100 ml"`` → ``"100ml"``).

    Parameters
    ----------
    name : str, optional
        The raw product name.  If `None` or empty, returns an empty
        string.

    Returns
    -------
    str
        The cleaned name.
    """
    if not name:
        return ""
    text = name.lower().strip()
    text = _strip_accents(text)
    # Replace hyphens and underscores with a space
    text = re.sub(r"[\s\-_]+", " ", text)
    # Remove any character that is not alphanumeric or space
    text = re.sub(r"[^a-z0-9 ]", "", text)
    # Join numbers with units (ml, g, mg, l)
    text = re.sub(r"(\d+)\s*(ml|g|mg|l)", r"\1\2", text)
    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_name_from_image_url(url: str) -> Optional[str]:
    """Recover a human‑readable product name from an image URL.

    Parapharma image filenames often encode the full product name in a
    slugified form (lowercase with hyphens).  When product names in
    HTML are truncated with an ellipsis (``"..."``), this helper can
    derive the likely full name by parsing the last path segment of
    the URL and converting it into a title‑cased string.

    Parameters
    ----------
    url : str
        The image URL (expected to end with ``.webp`` or another
        extension).

    Returns
    -------
    Optional[str]
        The inferred product name, or ``None`` if no slug could be
        extracted.
    """
    if not url:
        return None
    # Match the final path component before the extension.  We allow
    # letters, numbers, underscores and hyphens.  For example:
    # https://example.com/images/omeprazole-20-mg.webp -> omeprazole-20-mg
    match = re.search(r"/([\w\-]+)\.[a-zA-Z0-9]+$", url)
    if match:
        slug = match.group(1)
        # Replace hyphens and underscores with spaces and title case
        return slug.replace("-", " ").replace("_", " ").title()
    return None


def extract_size(clean_text: str) -> str:
    """Extract size token (e.g. ``"200ml"``) from a cleaned name.

    Parameters
    ----------
    clean_text : str
        A cleaned product name (as returned by :func:`clean_name`).

    Returns
    -------
    str
        The first size token found, or an empty string if none present.
    """
    match = re.search(r"(\d+(?:\.\d+)?)(ml|mg|g|l)", clean_text)
    return match.group(0) if match else ""


def extract_brand(
    clean_text: str,
    *,
    brands: Tuple[str, ...] = tuple(KNOWN_BRANDS),
    blacklist: Tuple[str, ...] = tuple(BRAND_BLACKLIST)
) -> Optional[str]:
    """Extract the brand name from a cleaned product name.

    The function tries to match the beginning of ``clean_text`` to one of
    the known brands (longest names first).  If no known brand matches,
    simple heuristics are applied: use the first token, or the first
    numeric token plus the next token.  Blacklisted tokens are ignored.

    Parameters
    ----------
    clean_text : str
        The cleaned product name.
    brands : tuple of str, optional
        A tuple of known brands.  The list should be sorted from longest
        to shortest names to ensure proper prefix matching.
    blacklist : tuple of str, optional
        A set of tokens that should never be considered a brand.

    Returns
    -------
    Optional[str]
        The extracted brand, or ``None`` if no brand could be determined.
    """
    text = clean_text.lower().strip()
    tokens = text.split()
    matched_brand = None
    # 1. Check for known brand prefixes
    for brand in brands:
        if text.startswith(brand):
            matched_brand = brand
            break
    # 2. Apply heuristics if no known brand
    if not matched_brand and tokens:
        if len(tokens) >= 2:
            if tokens[0] == "la" and tokens[1] not in blacklist:
                matched_brand = tokens[1]
            elif tokens[0].isdigit() and tokens[1] not in blacklist:
                matched_brand = f"{tokens[0]} {tokens[1]}"
            elif tokens[0] not in blacklist:
                matched_brand = tokens[0]
        else:
            if tokens[0] not in blacklist:
                matched_brand = tokens[0]
    # 3. If the brand is too short, extend with the next token
    if matched_brand and len(matched_brand.split()) == 1 and len(tokens) >= 2:
        first, second = tokens[0], tokens[1]
        candidate = f"{first} {second}"
        if candidate not in blacklist:
            matched_brand = candidate
    # 4. Final blacklist check
    if matched_brand and matched_brand.lower() in blacklist:
        return None
    return matched_brand


def normalize_availability(value: Optional[str]) -> str:
    """Normalise availability codes to ``"disponible"`` or ``"indisponible"``.

    Parameters
    ----------
    value : str, optional
        Raw availability string.  Common values include ``"in_stock"``,
        ``"out_of_stock"``, ``"disponible"`` and ``"rupture"``.

    Returns
    -------
    str
        ``"disponible"`` for available products, ``"indisponible"`` otherwise.
    """
    if not value:
        return "indisponible"
    mapping = {
        "in_stock": "disponible",
        "disponible": "disponible",
        "out_of_stock": "indisponible",
        "rupture": "indisponible",
        "indisponible": "indisponible",
    }
    return mapping.get(value.strip().lower(), "indisponible")


def clean_price(value: Optional[str]) -> Optional[float]:
    """Parse a price string into a float.

    The function removes any character that isn't a digit or comma, then
    replaces commas with dots and strips spaces before converting to
    float.  Returns ``None`` if the conversion fails.

    Parameters
    ----------
    value : str, optional
        Raw price string (e.g. ``"1 282,00 MAD"``).

    Returns
    -------
    Optional[float]
        The numeric price, or ``None`` on failure.
    """
    if value is None:
        return None
    # Remove everything except digits and commas
    cleaned = re.sub(r"[^\d,]", "", value)
    cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def map_category(cat: Optional[str]) -> str:
    """Map a raw category string to a canonical category.

    Uses :data:`category_mapping` defined in :mod:`.category_mapping`.
    Performs accent stripping and lower‑casing before searching for
    substrings.  If no mapping matches, returns ``"Autres"``.

    Parameters
    ----------
    cat : str, optional
        Raw category string.

    Returns
    -------
    str
        Canonical category.
    """
    if not cat:
        return "Autres"
    text = clean_name(cat)  # reuse clean_name to normalise
    for key, mapped in category_mapping.items():
        if key in text:
            return mapped
    return "Autres"