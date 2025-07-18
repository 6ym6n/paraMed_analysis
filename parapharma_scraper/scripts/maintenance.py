from pymongo import MongoClient
import re

client = MongoClient("mongodb://localhost:27017/")
db = client["paraMedProducts"]
collection = db["sr"]

def clean_name_from_image_url(url: str) -> str:
    match = re.search(r'/([\w\-]+)\.webp$', url)
    if match:
        name = match.group(1).replace("-", " ")
        return name.title()
    return None

def fix_truncated_names():
    query = { "name": { "$regex": r"\.\.\.$" }, "image_url": { "$exists": True } }
    count = 0
    for doc in collection.find(query):
        new_name = clean_name_from_image_url(doc.get("image_url", ""))
        if new_name and new_name.lower() not in doc["name"].lower():
            collection.update_one({ "_id": doc["_id"] }, { "$set": { "name": new_name } })
            count += 1
            print(f"✅ {doc['name']} → {new_name}")
    print(f"\n🔁 {count} noms corrigés.")

def delete_duplicates():
    duplicates = collection.aggregate([
        { "$group": {
            "_id": "$name",
            "dups": { "$addToSet": "$_id" },
            "count": { "$sum": 1 }
        }},
        { "$match": { "count": { "$gt": 1 } } }
    ])

    removed = 0
    for doc in duplicates:
        ids = doc["dups"]
        ids.pop(0)  # garde un seul doc
        result = collection.delete_many({ "_id": { "$in": ids } })
        removed += result.deleted_count
    print(f"🗑️ {removed} doublons supprimés.")

if __name__ == "__main__":
    print("🔧 Lancement de maintenance MongoDB")
    fix_truncated_names()
    delete_duplicates()
