# main.py

from mongo_utils import load_products, save_matches
from matcher import match_products
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

def main():
    print("🔍 Loading products...")
    parapharma = load_products("parapharma.ma")
    univers = load_products("universparadiscount.ma")

    print(f"🧼 Found {len(parapharma)} parapharma & {len(univers)} univers products")

    print("📦 Loading embedding model...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print("⚖️  Matching products...")
    matches = match_products(parapharma, univers, model)

    print("💾 Saving to MongoDB...")
    save_matches(matches)

    print("🎉 Done!")

if __name__ == "__main__":
    main()
