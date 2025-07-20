from pymongo import MongoClient
import unicodedata
import re
import json

# --- Normalisation du nom produit ---
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
sr = db["sr"]
univers = db["univers"]
merged = db["merged"]  # nouvelle collection fusionnée

# --- Vider la collection fusionnée si elle existe ---
merged.delete_many({})

# --- Traiter et insérer les produits ---
def process_and_insert(cursor, source):
    count = 0
    for doc in cursor:
        doc["site"] = source
        doc["clean_name"] = clean_name(doc.get("name", ""))
        doc.pop("_id", None)  # évite les conflits de _id
        doc.pop("source", None)
        merged.insert_one(doc)
        count += 1
    print(f"✅ {count} produits insérés depuis {source}")

if __name__ == "__main__":
    process_and_insert(sr.find(), "parapharma.ma")
    process_and_insert(univers.find(), "universparadiscount.ma")
    print("\n🔁 Fusion terminée dans paraMedProducts.merged")
