# post_scraping/scripts/categorize_products.py

from pymongo import MongoClient
from category_mapping import category_mapping
import unicodedata

# --- Fonction de normalisation et mapping ---
def normalize(text: str) -> str:
    return unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

def get_nouvelle_categorie(cat: str) -> str:
    cat = normalize((cat or "").strip().lower())
    for key, mapped in category_mapping.items():
        if key in cat:
            return mapped
    return "Autres"

# --- Connexion à la base MongoDB ---
client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
merged = db["para_univer_merged"]

# --- Application du mapping ---
count = 0
for doc in merged.find({}, {"category": 1}):
    old_cat = doc.get("category", "")
    new_cat = get_nouvelle_categorie(old_cat)
    merged.update_one(
        {"_id": doc["_id"]},
        {"$set": {"nouvelle_categorie": new_cat}}
    )
    count += 1

# --- Résultat ---
print(f"✅ {count} documents mis à jour avec la nouvelle catégorie.")
print("📦 Catégories détectées :", merged.distinct("nouvelle_categorie"))
