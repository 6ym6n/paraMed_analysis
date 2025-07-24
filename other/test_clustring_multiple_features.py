from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from tqdm import tqdm

# --- Connexion MongoDB ---
client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
collection = db["para_univer_merged"]
matched_collection = db["matched_products"]
matched_collection.delete_many({})  # Nettoyer les anciens résultats

# --- Charger les produits par catégorie et site ---
categories = collection.distinct("nouvelle_categorie")

model = SentenceTransformer("all-MiniLM-L6-v2")  # Léger et rapide

matches = []
used_univers_ids = set()  # Pour éviter les doublons

for cat in categories:
    print(f"🔍 Traitement catégorie : {cat}")

    pharma_docs = list(collection.find({"site": "parapharma.ma", "nouvelle_categorie": cat}))
    univers_docs = list(collection.find({"site": "universparadiscount.ma", "nouvelle_categorie": cat}))

    if not pharma_docs or not univers_docs:
        continue

    # Préparation des embeddings Univers avec marque incluse
    univers_names = [doc.get("clean_name", "") for doc in univers_docs]
    univers_brands = [doc.get("brand", doc.get("clean_name", "").split()[0] if doc.get("clean_name") else "") for doc in univers_docs]
    univers_features = [f"{brand} {name}" for brand, name in zip(univers_brands, univers_names)]
    univers_embeddings = model.encode(univers_features, convert_to_numpy=True)

    # Création de l'index FAISS
    dim = univers_embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(univers_embeddings)

    pharma_names = [doc.get("clean_name", "") for doc in pharma_docs]
    pharma_brands = [doc.get("brand", doc.get("clean_name", "").split()[0] if doc.get("clean_name") else "") for doc in pharma_docs]
    pharma_features = [f"{brand} {name}" for brand, name in zip(pharma_brands, pharma_names)]
    pharma_embeddings = model.encode(pharma_features, convert_to_numpy=True)

    # Recherche du voisin le plus proche
    D, I = index.search(pharma_embeddings, k=1)

    for i, pharma_doc in enumerate(pharma_docs):
        j = I[i, 0]
        score = D[i, 0]

        if j >= len(univers_docs):
            continue

        univers_doc = univers_docs[j]
        univers_id = univers_doc["_id"]

        # Vérifie si déjà utilisé
        if univers_id in used_univers_ids:
            continue

        name1 = pharma_doc.get("clean_name", "")
        name2 = univers_doc.get("clean_name", "")

        price1 = pharma_doc.get("price")
        price2 = univers_doc.get("price")

        if price1 is None or price2 is None:
            continue

        ecart = abs(price1 - price2)
        rel_diff = ecart / max(price1, price2)

        if rel_diff <= 0.1:
            matches.append({
                "nom_produit": name1,
                "brand": pharma_doc.get("brand", name1.split()[0] if name1 else None),
                "parapharma": {
                    "ma_prix": price1,
                    "ma_name": pharma_doc.get("name"),
                    "ma_url": pharma_doc.get("product_url")
                },
                "universparadiscount": {
                    "ma_prix": price2,
                    "ma_name": univers_doc.get("name"),
                    "ma_url": univers_doc.get("product_url")
                },
                "écart_max_min": round(ecart, 2)
            })

            used_univers_ids.add(univers_id)  # Marque comme utilisé

# --- Stockage en base MongoDB ---
if matches:
    matched_collection.insert_many(matches)
    print(f"\n✅ {len(matches)} correspondances insérées dans paraMedProducts.matched_products")
else:
    print("⚠️ Aucun match trouvé à insérer.")
