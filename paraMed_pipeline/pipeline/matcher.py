"""
Product matching engine.

This module implements a simple product matching algorithm based on
sentence embeddings.  Products from Parapharma and Univers are grouped
by brand and size; for each Parapharma product we compute an embedding
for the concatenated string of brand, clean_name and size and compare
it against candidate Univers products with the same brand and size.
Matches with cosine similarity above a configurable threshold are
returned.
"""

from __future__ import annotations

from typing import List, Dict, Tuple
from collections import defaultdict
import numpy as np

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from .utils.cleaning import clean_name
from ..config import EMBEDDING_MODEL, SIMILARITY_THRESHOLD


def create_matching_string(product: Dict) -> str:
    """Concatenate brand, clean_name and size for embedding."""
    parts = []
    brand = product.get("brand") or ""
    name = product.get("clean_name") or ""
    size = product.get("size") or ""
    for p in (brand, name, size):
        if p:
            parts.append(p)
    return " ".join(parts).strip()


def match_products(
    parapharma: List[Dict],
    univers: List[Dict],
    *,
    model: SentenceTransformer | None = None,
    similarity_threshold: float = SIMILARITY_THRESHOLD,
) -> List[Dict]:
    """Find matches between Parapharma and Univers products.

    Parameters
    ----------
    parapharma : list of dict
        Cleaned Parapharma products.
    univers : list of dict
        Cleaned Univers products.
    model : SentenceTransformer, optional
        Preloaded embedding model.  If omitted, the default model
        specified in :mod:`config` is loaded.
    similarity_threshold : float
        Minimum cosine similarity to consider a match.

    Returns
    -------
    list of dict
        List of match dictionaries with keys ``product_a`` (a
        Parapharma product), ``product_b`` (a Univers product) and
        ``similarity`` (a float).
    """
    if model is None:
        model = SentenceTransformer(EMBEDDING_MODEL)
    # Group Univers products by (brand, size)
    grouped: Dict[Tuple[str, str], List[Dict]] = defaultdict(list)
    for p in univers:
        key = ((p.get("brand") or "").lower(), (p.get("size") or "").lower())
        grouped[key].append(p)
    matches: List[Dict] = []
    for pa in parapharma:
        brand = (pa.get("brand") or "").lower()
        size = (pa.get("size") or "").lower()
        key = (brand, size)
        candidates = grouped.get(key, [])
        if not candidates:
            continue
        query_str = create_matching_string(pa)
        cand_strs = [create_matching_string(c) for c in candidates]
        if not cand_strs:
            continue
        emb_a = model.encode([query_str], normalize_embeddings=True)
        emb_b = model.encode(cand_strs, normalize_embeddings=True)
        sim_scores = cosine_similarity(emb_a, emb_b)[0]
        for idx, score in enumerate(sim_scores):
            if score >= similarity_threshold:
                matches.append({
                    "product_a": pa,
                    "product_b": candidates[idx],
                    "similarity": float(score),
                })
    return matches


__all__ = ["match_products"]