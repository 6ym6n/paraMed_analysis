from pymongo import MongoClient

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
collection = db["para_univer_merged"]

# Liste des marques connues (normalisées)
known_brands = [
    "la roche-posay", "la roche posay", "eau thermale avene", "vichy", "uriage", "cerave", "bioderma", "nuxe", "avene",
    "eucerin", "ducray", "klorane", "caudalie", "mustela", "filorga", "noreva", "topicrem", "isispharma", "embryolisse",
    "a-derma", "dermagor", "svr", "roger gallet", "neutrogena", "l'oreal", "loreal", "cetaphil", "bailleul", "biolane",
    "dermodex", "endocare", "lazartigue", "skinceuticals", "apivita", "melvita", "jacomo", "avril", "la provençale",
    "dr hauschka", "elancyl", "galénic", "weleda", "bcombio", "lierac", "johnson", "sanoflore", "revox", "revlon",
    "the ordinary", "biosecure", "marilou bio", "gamarde", "hydralin", "dermedic", "8882", "photo white"
]

# Supprimer doublons et trier par longueur
known_brands = sorted(set(known_brands), key=lambda x: -len(x))

# Liste noire : mots à ne jamais utiliser comme marque
blacklist = {
    'capteur', 'applicateur', 'pistolet', 'chaussettes', 'bracelet', 'brosse', 'boite', 'bandage',
    'coussin', 'coffret', 'sac', 'fauteuil', 'masque', 'huile', 'tube', 'thermoflash', 'appareil',
    'set', 'pack', 'ensemble', 'accessoire', 'stylo', 'support', 'chaise', 'lampe', 'table', 'tapis',
    'photo', 'oreiller', 'chausson', 'canne', 'bandelette', 'gant', 'collier', 'calecon', 'slip',
    'lit', 'bassin', 'couche', 'biberon', 'biberons', 'thermometre'
}

# Initialisation
updated = 0
unknown = []

for doc in collection.find({}, {"_id": 1, "clean_name": 1}):
    clean_name = doc.get("clean_name", "")
    clean_name_lower = clean_name.lower().strip()
    tokens = clean_name_lower.split()

    matched_brand = None

    # 1. Chercher si ça commence par une marque connue
    for brand in known_brands:
        if clean_name_lower.startswith(brand):
            matched_brand = brand
            break

    # 2. Sinon, heuristiques
    if not matched_brand and tokens:
        if len(tokens) >= 2:
            if tokens[0] == "la":
                matched_brand = tokens[1]
            elif tokens[0].isdigit():
                matched_brand = f"{tokens[0]} {tokens[1]}"
            else:
                matched_brand = tokens[0]
        elif len(tokens) == 1:
            matched_brand = tokens[0]

    # 3. Si marque très courte (≤ 2), tenter de l’étendre avec mot2
    if matched_brand and len(matched_brand) <= 2 and len(tokens) >= 2:
        matched_brand = f"{tokens[0]} {tokens[1]}"

    # 4. Exclure les marques blacklistées
    if matched_brand and matched_brand.lower() in blacklist:
        matched_brand = None

    # Mise à jour ou log des non reconnues
    if matched_brand:
        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"brand": matched_brand}}
        )
        updated += 1
    else:
        unknown.append(clean_name)

# Export des marques non reconnues
if unknown:
    with open("unknown_brands.txt", "w", encoding="utf-8") as f:
        for name in unknown:
            f.write(name + "\n")

print(f"✅ {updated} documents mis à jour avec le champ 'brand'")
print(f"📝 {len(unknown)} produits sans marque connue ont été enregistrés dans 'unknown_brands.txt'")
