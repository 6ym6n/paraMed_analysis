from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
mapara = db["mapara"]
merged = db["merged"]

count = 0

for doc in mapara.find():
    doc.pop("_id", None)  # éviter conflit de clé primaire
    doc["site"] = "mapara.ma"
    merged.insert_one(doc)
    count += 1

print(f"✅ {count} produits ajoutés à la collection 'merged'")
