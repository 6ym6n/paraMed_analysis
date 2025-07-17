# utils/mongo.py

from pymongo import MongoClient

def get_mongo_collection(db_name="paraMedProducts", collection_name="sr"):
    client = MongoClient("mongodb://localhost:27017/")
    db = client[db_name]
    return db[collection_name]
