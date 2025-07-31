from pymongo import MongoClient

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
collection = db["para_univer_merged"]

# Extraire toutes les valeurs distinctes du champ 'brand'
brands = collection.distinct("brand")

# Trier alphabétiquement
brands = sorted(set(brands))

# Enregistrer dans un fichier texte
with open("brands_detected.txt", "w", encoding="utf-8") as f:
    for b in brands:
        f.write(b.strip().lower() + "\n")

print(f"✅ {len(brands)} marques distinctes exportées dans 'brands_detected.txt'")
