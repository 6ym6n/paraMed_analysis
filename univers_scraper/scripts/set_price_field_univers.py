from pymongo import MongoClient

def update_price_field():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["paraMedProducts"]
    collection = db["univers"]

    result = collection.update_many(
        {},
        [
            {
                "$set": {
                    "price": {
                        "$cond": [
                            {
                                "$and": [
                                    { "$ne": ["$discounted_price", None] },
                                    { "$ne": ["$discounted_price", ""] }
                                ]
                            },
                            "$discounted_price",
                            "$original_price"
                        ]
                    }
                }
            }
        ]
    )

    print(f"✅ {result.modified_count} documents mis à jour avec le champ 'price'.")

if __name__ == "__main__":
    update_price_field()
