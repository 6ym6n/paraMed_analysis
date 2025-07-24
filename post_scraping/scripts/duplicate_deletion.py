from pymongo import MongoClient

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
collection = db["para_univer_merged"]

# Pipeline d'agrégation pour trouver les doublons (même site + clean_name)
pipeline = [
    {
        "$group": {
            "_id": {"site": "$site", "clean_name": "$clean_name"},
            "ids": {"$addToSet": "$_id"},
            "count": {"$sum": 1}
        }
    },
    {
        "$match": {
            "count": {"$gt": 1}
        }
    }
]

duplicates = list(collection.aggregate(pipeline))

# Suppression : garder un seul ID par groupe
deleted_count = 0
for group in duplicates:
    ids = group["ids"]
    ids_to_delete = ids[1:]  # Garder le premier, supprimer les autres
    result = collection.delete_many({"_id": {"$in": ids_to_delete}})
    deleted_count += result.deleted_count

print(f"🗑️ {deleted_count} doublons supprimés (par site + clean_name)")
