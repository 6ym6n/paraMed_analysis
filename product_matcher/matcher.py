# matcher.py

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from preprocess import create_matching_string
from config import SIMILARITY_THRESHOLD
from collections import defaultdict
import numpy as np

def group_by_brand_size(products):
    grouped = defaultdict(list)
    for p in products:
        key = (p.get("brand", "").lower(), p.get("size", "").lower())
        grouped[key].append(p)
    return grouped

def match_products(parapharma, univers, model):
    print("→ Grouping universparadiscount.ma by (brand, size)...")
    grouped_univers = group_by_brand_size(univers)

    matches = []
    skipped = 0

    for p in parapharma:
        brand = p.get("brand", "").lower()
        size = p.get("size", "").lower()
        key = (brand, size)

        candidates = grouped_univers.get(key, [])
        if not candidates:
            skipped += 1
            continue

        emb_a = model.encode([create_matching_string(p)], normalize_embeddings=True)
        emb_b = model.encode([create_matching_string(c) for c in candidates], normalize_embeddings=True)

        sim_scores = cosine_similarity(emb_a, emb_b)[0]
        for idx, score in enumerate(sim_scores):
            if score >= SIMILARITY_THRESHOLD:
                matches.append({
                    "product_a": p,
                    "product_b": candidates[idx],
                    "similarity": float(score)
                })

    print(f"✅ {len(matches)} matches found")
    print(f"⏭️ Skipped {skipped} parapharma products with no same brand & size in universparadiscount")
    return matches
