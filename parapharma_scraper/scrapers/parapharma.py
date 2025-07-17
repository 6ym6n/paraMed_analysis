# scrapers/parapharma.py (complément)

import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_category_page(base_category_url, category_name, max_pages=100):
    all_results = []
    page = 21

    while page <= max_pages:
        url = f"{base_category_url}?page={page}"
        print(f"🔎 Scraping {category_name} - page {page}: {url}")

        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Erreur HTTP {response.status_code} sur {url}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        product_cards = soup.select(".product-miniature")
        if not product_cards:
            print(f"🚫 Fin de la pagination (aucun produit trouvé)")
            break

        for card in product_cards:
            try:
                name = card.select_one("h2.h3.product-title").get_text(strip=True)

                # Prix actuel
                price_text = card.select_one("span.price").get_text(strip=True)
                price = float(price_text.replace("DHS", "").replace("\xa0", "").replace(" ", "").strip())
                
                # Promo éventuelle
                discount_tag = card.select_one("span.discount-amount.discount-product")
                discount = None
                original_price = price
                if discount_tag:
                    discount_text = discount_tag.get_text(strip=True).replace("DHS", "").replace("\xa0", "").replace("-", "").replace(" ", "")
                    discount = float(discount_text)
                    original_price = round(price + discount, 2)
                

                # Disponibilité
                out_of_stock = card.select_one("li.product-flag.out_of_stock") is not None
                availability = "rupture" if out_of_stock else "disponible"

                # URL produit
                link = "https://parapharma.ma" + card.select_one("a")["href"]

                # Image
                image_tag = card.select_one("img.img-fluid")
                image_url = image_tag["src"] if image_tag else None

                date = datetime.now().strftime("%Y-%m-%d")

                all_results.append({
                    "site": "parapharma.ma",
                    "category": category_name,
                    "name": name,
                    "price": price,
                    "discount": discount,
                    "original_price": original_price,
                    "availability": availability,
                    "url": link,
                    "image_url": image_url,
                    "scraped_at": date
                })

            except Exception as e:
                print(f"⚠️ Erreur sur un produit : {e}")

        page += 1

    return all_results
