import requests
from bs4 import BeautifulSoup
import json
import time
import re
import unicodedata
from pymongo import MongoClient

# --- Clean name builder ---
def clean_name(name):
    if not name:
        return ""
    name = name.lower()
    name = unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode("utf-8")
    name = re.sub(r"[\s\-_]+", " ", name)
    name = re.sub(r"[^a-z0-9 ]", "", name)
    name = re.sub(r"(\d+)\s*(ml|g|mg|l)", r"\1\2", name)
    return name.strip()

# --- Price cleaner ---
def clean_price(text):
    if not text:
        return None
    text = text.replace("\xa0", "").replace("dh", "").replace(",", ".")
    return float(re.sub(r"[^0-9.]", "", text))

# --- MongoDB setup ---
client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
collection = db["novapara"]

# --- Scraper function ---
def scrape_category(name, url):
    print(f"🔍 Catégorie: {name}")
    page = 1
    total_scraped = 0

    while page <= 200:
        paged_url = f"{url}?page={page}"
        print(f"  ➜ Page {page}...")
        res = requests.get(paged_url)
        if res.status_code != 200:
            break

        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select("div.sf__col-item")
        if not items:
            break

        for item in items:
            try:
                product = {"category": name, "site": "novapara.ma"}

                # Nom + URL produit
                name_tag = item.select_one("a.sf__pcard-name")
                product["name"] = name_tag.get_text(strip=True) if name_tag else None
                product["product_url"] = (
                    "https://novapara.ma" + name_tag.get("href") if name_tag and name_tag.get("href") else None
                )

                # Image
                img_tag = item.select_one("img.se-out")
                product["image_url"] = ("https:" + img_tag.get("src") if img_tag and img_tag.get("src") else None)

                # Prix remisé (discounted)
                disc_price_tag = item.select_one("span.prod__price")
                product["discounted_price"] = clean_price(disc_price_tag.text) if disc_price_tag else None

                # Prix barré (original)
                orig_price_tag = item.select_one("span.prod__compare_price")
                product["original_price"] = clean_price(orig_price_tag.text) if orig_price_tag else None

                # Réduction
                reduc_tag = item.select_one("span.prod__tag-discounted")
                product["reduction"] = reduc_tag.text.strip() if reduc_tag else None

                # clean_name (nom unique nettoyé)
                product["clean_name"] = clean_name(product["name"])

                # Prix final à utiliser
                if product["discounted_price"] is not None:
                    product["price"] = product["discounted_price"]
                else:
                    product["price"] = product["original_price"]

                # Insertion Mongo
                collection.update_one(
                    {"product_url": product["product_url"]},
                    {"$set": product},
                    upsert=True
                )
                total_scraped += 1

            except Exception as e:
                print(f"⚠️ Erreur produit: {e}")

        page += 1
        time.sleep(1)

    print(f"✅ {total_scraped} produits récupérés pour '{name}'\n")

# --- Main ---
if __name__ == "__main__":
    with open("../data/main_categories.json", encoding="utf-8") as f:
        categories = json.load(f)

    for cat in categories:
        scrape_category(cat["name"], cat["url"])
