import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
collection = db["mapara"]

# --- Price cleaner ---
def clean_price(text):
    if not text:
        return None
    text = text.replace("\xa0", "").replace("MAD", "").replace(",", ".")
    return float(re.sub(r"[^0-9.]", "", text))

# --- Scraper function ---
def scrape_category(name, url):
    print(f"🔍 Catégorie: {name}")
    page = 1
    total_scraped = 0

    while page <= 25:
        paged_url = f"{url}?page={page}"
        print(f"  ➜ Page {page}...")
        res = requests.get(paged_url)
        if res.status_code != 200:
            break

        soup = BeautifulSoup(res.text, "html.parser")
        articles = soup.select("article.js-product-miniature")
        if not articles:
            break

        for art in articles:
            try:
                product = {"category": name, "site": "mapara.ma"}

                # Nom du produit
                name_tag = art.select_one("h3.s_title_block a")
                product["name"] = name_tag.get("title") if name_tag else None

                # URL produit
                product["product_url"] = name_tag.get("href") if name_tag else None

                # Image
                img_tag = art.select_one("img.front-image")
                product["image_url"] = img_tag.get("src") if img_tag else None

                # Marque
                brand_tag = art.select_one("div.pro_list_manufacturer")
                product["brand"] = brand_tag.get_text(strip=True) if brand_tag else None

                # Prix promo
                discounted_tag = art.select_one("span.price.st_discounted_price")
                product["discounted_price"] = clean_price(discounted_tag.text) if discounted_tag else None

                # Prix original
                original_tag = art.select_one("span.regular-price")
                product["original_price"] = clean_price(original_tag.text) if original_tag else None

                # Réduction en %
                reduction_tag = art.select_one("span.price-percent-reduction")
                product["reduction"] = reduction_tag.text.strip() if reduction_tag else None

                # Calcul du champ de prix final (logique comme univers)
                if product["discounted_price"] is not None:
                    product["price"] = product["discounted_price"]
                else:
                    product["price"] = product["original_price"]

                # Insertion MongoDB
                collection.update_one(
                    {"product_url": product["product_url"]},
                    {"$set": product},
                    upsert=True
                )
                total_scraped += 1

            except Exception as e:
                print(f"⚠️ Erreur sur un produit: {e}")

        page += 1
        time.sleep(1)

    print(f"✅ {total_scraped} produits récupérés pour '{name}'\n")

if __name__ == "__main__":
    with open("../data/main_categories.json", encoding="utf-8") as f:
        categories = json.load(f)

    for cat in categories:
        scrape_category(cat["name"], cat["url"])
