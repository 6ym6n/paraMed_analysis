import requests
from bs4 import BeautifulSoup
import json
import os

def get_navbar_categories():
    url = "https://parapharma.ma/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    menu_items = soup.select("ul.mm_menus_ul a[href]")
    categories = []

    for item in menu_items:
        link = item.get("href")
        name = item.get_text(strip=True)

        if link and name:
            if "/10-" in link or "/11-" in link or "/12-" in link:  # catégories principales
                full_url = link if link.startswith("http") else f"https://parapharma.ma{link}"
                categories.append({"name": name, "url": full_url})

    return categories

if __name__ == "__main__":
    cats = get_navbar_categories()

    os.makedirs("data", exist_ok=True)

    with open("data/categories.json", "w", encoding="utf-8") as f:
        json.dump(cats, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(cats)} catégories enregistrées dans data/categories.json")
