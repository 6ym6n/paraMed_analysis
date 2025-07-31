from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
collection = db["para_univer_merged"]

# Fichier de sortie
output_file = "short_brands_review.txt"

# Ouvrir le fichier en écriture
with open(output_file, "w", encoding="utf-8") as f:
    f.write("📋 Marques très courtes (≤ 2 caractères) avec clean_name associé :\n\n")

    # Requête Mongo : brands de longueur ≤ 2
    query = {
        "brand": {"$exists": True, "$ne": None},
        "$expr": {"$lte": [{"$strLenCP": "$brand"}, 2]}
    }

    # Projection : brand + clean_name
    projection = {"brand": 1, "clean_name": 1}

    # Récupérer et écrire
    for doc in collection.find(query, projection):
        brand = doc.get("brand", "").strip()
        clean = doc.get("clean_name", "").strip()
        f.write(f"Brand: {brand:<3} | Clean Name: {clean}\n")

print(f"✅ Export terminé : {output_file}")
