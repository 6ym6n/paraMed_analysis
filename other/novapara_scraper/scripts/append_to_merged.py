from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
novapara = db["novapara"]
merged = db["merged"]

count = 0

for doc in novapara.find():
    doc.pop("_id", None)
    doc["site"] = "novapara.ma"
    merged.insert_one(doc)
    count += 1

print(f"✅ {count} produits ajoutés à la collection 'merged' depuis novapara")
