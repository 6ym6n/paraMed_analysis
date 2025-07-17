import json
from scrapers.parapharma import scrape_category_page
from utils.mongo import get_mongo_collection

def main():
    with open("scripts/data/categories.json", encoding="utf-8") as f:
        categories = json.load(f)

    collection = get_mongo_collection()

    for cat in categories:
        print(f"\n📁 Scraping catégorie : {cat['name']}")
        produits = scrape_category_page(cat["url"], cat["name"])
        if produits:
            collection.insert_many(produits)
            print(f"✅ {len(produits)} produits ajoutés ({cat['name']})")
        else:
            print(f"⚠️ Aucun produit trouvé dans {cat['name']}")

if __name__ == "__main__":
    main()
