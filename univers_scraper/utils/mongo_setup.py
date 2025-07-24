# Connexion MongoDB pour univers_scraper

from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def get_mongo_client():
    """
    Retourne un client MongoDB
    """
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    try:
        client = MongoClient(mongo_uri)
        # Test de connexion
        client.admin.command('ping')
        print("✅ Connexion MongoDB établie")
        return client
    except Exception as e:
        print(f"❌ Erreur de connexion MongoDB : {e}")
        return None

def get_database(client, db_name=None):
    """
    Retourne la base de données
    """
    if not client:
        return None
    
    db_name = db_name or os.getenv('MONGO_DB_NAME', 'universProducts')
    return client[db_name]

def get_collection(db, collection_name='products'):
    """
    Retourne la collection
    """
    if not db:
        return None
    return db[collection_name]

def setup_mongo_connection():
    """
    Configuration complète de la connexion MongoDB
    """
    client = get_mongo_client()
    if client:
        db = get_database(client)
        collection = get_collection(db)
        return client, db, collection
    return None, None, None
