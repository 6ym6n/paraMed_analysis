from pymongo import MongoClient
import re

def extract_size(text):
    text = text.lower()  # pour attraper "ML", "Ml", etc.
    match = re.search(r'(\d+(?:\.\d+)?)(ml|mg|g|l)', text)
    return match.group(0) if match else ""

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
collection = db["para_univer_merged"]

updated = 0
for doc in collection.find({}, {"_id": 1, "clean_name": 1}):
    clean_name = doc.get("clean_name", "")
    size = extract_size(clean_name)
    collection.update_one(
        {"_id": doc["_id"]},
        {"$set": {"size": size}}
    )
    updated += 1

print(f"✅ {updated} documents mis à jour avec le champ 'size'")
