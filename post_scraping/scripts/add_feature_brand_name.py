from pymongo import MongoClient

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
collection = db["para_univer_merged"]

# Mise à jour des documents
updated = 0
for doc in collection.find({}, {"_id": 1, "clean_name": 1}):
    clean_name = doc.get("clean_name", "")
    brand = clean_name.split()[0] if clean_name else None

    if brand:
        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"brand": brand}}
        )
        updated += 1

print(f"✅ {updated} documents mis à jour avec le champ 'brand'")
