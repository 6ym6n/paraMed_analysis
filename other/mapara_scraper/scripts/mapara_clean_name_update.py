from pymongo import MongoClient
import unicodedata
import re

# --- Clean name builder ---
def clean_name(name):
    if not name:
        return ""
    name = name.lower()
    name = unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode("utf-8")
    name = re.sub(r"[\s\-_]+", " ", name)
    name = re.sub(r"[^a-z0-9 ]", "", name)
    name = re.sub(r"(\d+)\s*(ml|g|mg|l)", r"\1\2", name)
    return name.strip()

# --- Connexion MongoDB ---
client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
collection = db["mapara"]

# --- Mise à jour des clean_name ---
count = 0
for doc in collection.find():
    name = doc.get("name", "")
    brand = doc.get("brand", "")
    full_name = f"{brand} {name}".strip()
    clean = clean_name(full_name)

    result = collection.update_one(
        {"_id": doc["_id"]},
        {"$set": {"clean_name": clean}}
    )
    count += result.modified_count

print(f"✅ {count} produits mis à jour avec le champ clean_name")
