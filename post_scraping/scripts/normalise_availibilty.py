from pymongo import MongoClient

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
collection = db["para_univer_merged"]

# Mappage des valeurs à normaliser
mapping = {
    "in_stock": "disponible",
    "disponible": "disponible",
    "out_of_stock": "indisponible",
    "rupture": "indisponible"
}

# Mise à jour des documents
updated = 0
for old_value, new_value in mapping.items():
    result = collection.update_many(
        {"availability": old_value},
        {"$set": {"availability": new_value}}
    )
    updated += result.modified_count

print(f"✅ {updated} documents mis à jour dans 'availability'")
