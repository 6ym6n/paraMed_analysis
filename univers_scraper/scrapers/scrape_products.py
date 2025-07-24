import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import json
from pymongo import MongoClient
import re

# MongoDB setup
client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
collection = db["univers"]

# Helper to clean price strings like '1 282,00 MAD'
def clean_price(text):
    if not text:
        return None
    cleaned = re.sub(r"[^\d,]", "", text)  # Remove non-numeric except comma
    cleaned = cleaned.replace(",", ".").replace(" ", "")
    try:
        return float(cleaned)
    except ValueError:
        return None

# Scraper for one page of category
def scrape_category_page(category_name, category_url):
    products = []
    page = 1
    while page <= 1:
        url = f"{category_url}?resultsPerPage=3846&page={page}"
        print(f"🔍 Scraping {url}")

        res = requests.get(url)
        if res.status_code != 200:
            break

        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select("div.item")
        if not items:
            break  # No more products

        for item in items:
            try:
                product = {"source": "universparadiscount.ma"}

                name_tag = item.select_one(".product_name a")
                product["name"] = name_tag["title"] if name_tag else None

                product_url = name_tag["href"] if name_tag else None
                product["product_url"] = product_url

                img_tag = item.select_one("img.ax-img-loader")
                product["image_url"] = img_tag["src"] if img_tag else None

                category_tag = item.select_one(".ax-product-cats a")
                product["category"] = category_tag.get_text(strip=True) if category_tag else category_name

                original_price_tag = item.select_one("span.regular-price")
                discounted_price_tag = item.select_one("span.price")

                product["original_price"] = clean_price(original_price_tag.text) if original_price_tag else None
                product["discounted_price"] = clean_price(discounted_price_tag.text) if discounted_price_tag else product["original_price"]

                flags = item.select(".label-flag")
                product["is_discounted"] = any("type-discount" in f["class"] for f in flags)
                product["is_out_of_stock"] = any("type-out_of_stock" in f["class"] for f in flags)

                collection.update_one(
                    {"product_url": product["product_url"]},
                    {"$set": product},
                    upsert=True
                )
                products.append(product)

            except Exception as e:
                print(f"⚠️ Erreur produit: {e}")

        page += 1
        time.sleep(1)

    print(f"✅ {len(products)} produits trouvés dans {category_name}\n")
    return products

if __name__ == "__main__":
    with open("data/univers_main_categories_filtered.json", encoding="utf-8") as f:
        categories = json.load(f)

    for cat in categories:
        scrape_category_page(cat["name"], cat["url"])
