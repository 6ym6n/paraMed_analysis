import requests
from bs4 import BeautifulSoup
import json
import os

def get_main_categories():
    url = "https://universparadiscount.ma/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    categories = []
    menu_links = soup.select("a.ets_mm_url[href]")

    for link in menu_links:
        name = link.get_text(strip=True)
        href = link["href"]
        if name and href.startswith("http"):
            categories.append({
                "name": name,
                "url": href
            })

    return categories

if __name__ == "__main__":
    categories = get_main_categories()

    os.makedirs("data", exist_ok=True)

    with open("data/univers_main_categories.json", "w", encoding="utf-8") as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(categories)} catégories enregistrées dans data/univers_main_categories.json")
