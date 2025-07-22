from pymongo import MongoClient
import unicodedata
import re
from datetime import datetime

# --- Normalisation du nom produit ---
def clean_name(name):
    if not name:
        return ""
    name = name.lower()
    name = unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode("utf-8")
    name = re.sub(r"[\s\-_]+", " ", name)
    name = re.sub(r"[^a-z0-9 ]", "", name)
    name = re.sub(r"(\d+)\s*(ml|g|mg|l)", r"\1\2", name)
    return name.strip()

# --- Connexion MongoDB ---
client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
sr = db["sr"]
univers = db["univers"]
merged = db["para_univer_merged"]

# --- Vider la collection fusionnée si elle existe ---
merged.delete_many({})

def process_and_insert(cursor, source):
    count = 0
    for doc in cursor:
        # --- Site d'origine ---
        site = source

        # --- URL produit ---
        product_url = doc.get("product_url") or doc.get("url") or ""

        # --- Catégorie (tout en minuscules) ---
        category = (doc.get("category") or "").strip().lower()

        # --- Nom original & nettoyé ---
        name = (doc.get("name") or "").strip()
        clean = clean_name(name)

        # --- Prix courant & original ---
        if doc.get("is_discounted") and "discounted_price" in doc:
            price = doc["discounted_price"]
        else:
            price = doc.get("price")

        original_price = doc.get("original_price")

        # --- Calcul du montant et flag de remise ---
        discount = None
        is_discounted = False
        if original_price is not None and price is not None:
            discount = original_price - price
            is_discounted = discount > 0

        # --- Disponibilité ---
        if "availability" in doc:
            availability = doc["availability"]
        else:
            availability = "out_of_stock" if doc.get("is_out_of_stock") else "in_stock"

        # --- Image ---
        image_url = doc.get("image_url", "")

        # --- Date de scraping (parsed en datetime) ---
        scraped_at_str = doc.get("scraped_at")
        if scraped_at_str:
            try:
                scraped_at_dt = datetime.fromisoformat(scraped_at_str)
            except ValueError:
                scraped_at_dt = datetime.utcnow()
        else:
            scraped_at_dt = datetime.utcnow()

        # --- Nouveau document unifié ---
        new_doc = {
            "site": site,
            "product_url": product_url,
            "category": category,
            "name": name,
            "clean_name": clean,
            "price": price,
            "original_price": original_price,
            "discount": discount,
            "is_discounted": is_discounted,
            "availability": availability,
            "image_url": image_url,
            "scraped_at": scraped_at_dt,
        }

        merged.insert_one(new_doc)
        count += 1

    print(f"✅ {count} produits insérés depuis {source}")

    count = 0
    for doc in cursor:
        # --- Site d'origine ---
        site = source

        # --- URL produit ---
        product_url = doc.get("product_url") or doc.get("url") or ""

        # --- Catégorie (tout en minuscules) ---
        category = doc.get("category", "").strip().lower()

        # --- Nom original & nettoyé ---
        name = doc.get("name", "").strip()
        clean = clean_name(name)

        # --- Prix courant & original ---
        # si discounted_price existe et is_discounted=True, on l'utilise, sinon on prend price
        price = None
        if doc.get("is_discounted") and "discounted_price" in doc:
            price = doc["discounted_price"]
        else:
            price = doc.get("price")

        original_price = doc.get("original_price")

        # --- Calcul du montant et flag de remise ---
        discount = None
        is_discounted = False
        if original_price is not None and price is not None:
            discount = original_price - price
            is_discounted = discount > 0

        # --- Disponibilité ---
        if "availability" in doc:
            availability = doc["availability"]
        else:
            availability = "out_of_stock" if doc.get("is_out_of_stock") else "in_stock"

        # --- Image ---
        image_url = doc.get("image_url", "")

        # --- Date de scraping (parsed en datetime) ---
        scraped_at_str = doc.get("scraped_at")
        if scraped_at_str:
            try:
                scraped_at_dt = datetime.fromisoformat(scraped_at_str)
            except ValueError:
                scraped_at_dt = datetime.utcnow()
        else:
            scraped_at_dt = datetime.utcnow()

        # --- Nouveau document unifié ---
        new_doc = {
            "site": site,
            "product_url": product_url,
            "category": category,
            "name": name,
            "clean_name": clean,
            "price": price,
            "original_price": original_price,
            "discount": discount,
            "is_discounted": is_discounted,
            "availability": availability,
            "image_url": image_url,
            "scraped_at": scraped_at_dt,
        }

        merged.insert_one(new_doc)
        count += 1

    print(f"✅ {count} produits insérés depuis {source}")

if __name__ == "__main__":
    process_and_insert(sr.find(), "parapharma.ma")
    process_and_insert(univers.find(), "universparadiscount.ma")
    print("\n🔁 Fusion terminée dans paraMedProducts.para_univer_merged")
