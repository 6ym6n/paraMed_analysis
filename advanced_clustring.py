from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from rapidfuzz import fuzz
from tqdm import tqdm
import re
import uuid

def extract_size(text):
    m = re.search(r'(\\d+(\\.\\d+)?)(ml|mg|g|l)', text)
    return m.group(0) if m else ""

def size_match(size1, size2):
    return 1 if size1 and size2 and size1 == size2 else 0

# --- Connexion MongoDB ---
client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
collection = db["para_univer_merged"]
out_collection = db["product_clusters"]
out_collection.delete_many({})

model = SentenceTransformer("all-MiniLM-L6-v2")

brands = collection.distinct("brand")
cats = collection.distinct("nouvelle_categorie")

clusters = []
used_univers = set()

for brand in tqdm(brands, desc="Brands"):
    for cat in cats:
        pharma_docs_all = list(collection.find({"site": "parapharma.ma", "brand": brand, "nouvelle_categorie": cat}))
        univers_docs_all = list(collection.find({"site": "universparadiscount.ma", "brand": brand, "nouvelle_categorie": cat}))
        if not pharma_docs_all or not univers_docs_all:
            continue

        pharma_sizes = set(extract_size(doc.get("clean_name", "")) for doc in pharma_docs_all)
        univers_sizes = set(extract_size(doc.get("clean_name", "")) for doc in univers_docs_all)
        sizes = pharma_sizes.union(univers_sizes)
        if not sizes: sizes = {""}

        for size in sizes:
            pharma_docs = [doc for doc in pharma_docs_all if extract_size(doc.get("clean_name", "")) == size]
            univers_docs = [doc for doc in univers_docs_all if extract_size(doc.get("clean_name", "")) == size]
            if not pharma_docs or not univers_docs:
                continue

            pharma_names = [doc.get("clean_name", "") for doc in pharma_docs]
            pharma_embeddings = model.encode(pharma_names, convert_to_numpy=True, normalize_embeddings=True)

            univers_names = [doc.get("clean_name", "") for doc in univers_docs]
            univers_embeddings = model.encode(univers_names, convert_to_numpy=True, normalize_embeddings=True)

            dim = univers_embeddings.shape[1]
            index = faiss.IndexFlatIP(dim)
            index.add(univers_embeddings)

            k = min(7, len(univers_docs))
            scores, idxs = index.search(pharma_embeddings, k)

            for i, pharma_doc in enumerate(pharma_docs):
                name1 = pharma_doc.get("clean_name", "")
                price1 = pharma_doc.get("price")
                size1 = extract_size(name1)
                for neighbor in range(k):
                    j = idxs[i, neighbor]
                    sim = float(scores[i, neighbor])

                    if j >= len(univers_docs):
                        continue

                    univers_doc = univers_docs[j]
                    name2 = univers_doc.get("clean_name", "")
                    price2 = univers_doc.get("price")
                    size2 = extract_size(name2)
                    univers_id = univers_doc["_id"]

                    if univers_id in used_univers:
                        continue

                    if price1 is None or price2 is None:
                        continue

                    fuzzy_score = float(fuzz.token_set_ratio(name1, name2) / 100)
                    rel_diff = abs(price1 - price2) / max(price1, price2)
                    price_sim = float(1 - rel_diff) if rel_diff <= 0.4 else 0.0
                    size_sim = float(size_match(size1, size2))

                    final_score = float(0.5 * sim + 0.25 * fuzzy_score + 0.2 * price_sim + 0.05 * size_sim)

                    if final_score > 0.87:
                        cluster_id = str(uuid.uuid4())
                        clusters.append({
                            "cluster_id": cluster_id,
                            "brand": brand,
                            "nouvelle_categorie": cat,
                            "size": size1,
                            "final_score": final_score,
                            "parapharma": {
                                "id": str(pharma_doc["_id"]),
                                "name": pharma_doc.get("name"),
                                "clean_name": name1,
                                "price": float(price1),
                                "url": pharma_doc.get("product_url")
                            },
                            "universparadiscount": {
                                "id": str(univers_doc["_id"]),
                                "name": univers_doc.get("name"),
                                "clean_name": name2,
                                "price": float(price2),
                                "url": univers_doc.get("product_url")
                            }
                        })
                        used_univers.add(univers_id)
                        break  # Passe au produit suivant parapharma

# Sécurité : conversion float globale (parano)
for c in clusters:
    c["final_score"] = float(c["final_score"])
    c["parapharma"]["price"] = float(c["parapharma"]["price"])
    c["universparadiscount"]["price"] = float(c["universparadiscount"]["price"])

if clusters:
    out_collection.insert_many(clusters)
    print(f"✅ {len(clusters)} clusters exportés dans paraMedProducts.product_clusters")
else:
    print('⚠️ Aucun cluster trouvé.')
