import json
import os

# Catégories à garder (en majuscules sans accents ni espaces inutiles)
CATEGORIES_VALIDES = {
    "DERMOCOSMÉTIQUE",
    "CHEVEUX",
    "VISAGE",
    "MAQUILLAGE",
    "CORPS",
    "BÉBÉ&MAMAN",
    "SANTÉ",
    "HOMME",
    "PRODUITS CORÉENS",
}

# Normalise les noms pour une comparaison robuste
def normalize(name):
    return (
        name.replace("É", "E")
            .replace("À", "A")
            .replace("È", "E")
            .replace("&", "&")
            .replace("-", " ")
            .strip()
            .upper()
    )

if __name__ == "__main__":
    input_file = "data/univers_main_categories.json"
    output_file = "data/univers_main_categories_filtered.json"

    with open(input_file, encoding="utf-8") as f:
        categories = json.load(f)

    filtered = [
        cat for cat in categories
        if normalize(cat["name"]) in map(normalize, CATEGORIES_VALIDES)
    ]

    os.makedirs("data", exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(filtered)} catégories gardées dans {output_file}")
