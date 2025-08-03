# mongo_utils.py

from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, COLLECTION_NAME, MATCHES_COLLECTION

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def load_products(site_name):
    return list(db[COLLECTION_NAME].find({"site": site_name}))

def save_matches(matches):
    if matches:
        db[MATCHES_COLLECTION].insert_many(matches)
