from pymongo import MongoClient

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
collection = db["para_univer_merged"]

# Liste des marques connues (normalisées en minuscules, sans accents ni majuscules)
known_brands = [
    "la roche-posay", "vichy", "uriage", "cerave", "bioderma", "nuxe", "avene", "eucerin", "ducray",
    "klorane", "caudalie", "mustela", "filorga", "noreva", "topicrem", "isispharma", "embryolisse",
    "a-derma", "dermagor", "svr", "roger gallet", "neutrogena", "l'oreal", "loreal", "cetaphil",
    "bailleul", "biolane", "dermodex", "endocare", "lazartigue", "uriage", "skinceuticals", "apivita",
    "ducray", "melvita", "jacomo", "avril", "la provençale", "dr hauschka", "elancyl", "galénic",
    "weleda", "bcombio", "lierac", "johnson", "topicrem", "sanoflore", "revox", "revlon", "the ordinary",
    "cerave", "biosecure", "marilou bio", "gamarde", "lafrocheposay", "uriage", "la roche posay",
    "eau thermale avene", "uriage", "bioderma", "hydralin", "dermedic"
]

# Normalisation : retirer les doublons et trier par longueur descendante (pour matcher les marques longues d'abord)
known_brands = sorted(set(known_brands), key=lambda x: -len(x))

# Mise à jour des documents
updated = 0

for doc in collection.find({}, {"_id": 1, "clean_name": 1}):
    clean_name = doc.get("clean_name", "")
    clean_name_lower = clean_name.lower().strip()

    matched_brand = None

    # Recherche de la marque connue au début du clean_name
    for brand in known_brands:
        if clean_name_lower.startswith(brand):
            matched_brand = brand
            break

    # Si aucune marque connue, appliquer la règle "la + 2e mot"
    if not matched_brand:
        tokens = clean_name_lower.split()
        if len(tokens) >= 2 and tokens[0] == "la":
            matched_brand = tokens[1]
        elif len(tokens) >= 1:
            matched_brand = tokens[0]

    # Mise à jour du champ brand
    if matched_brand:
        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"brand": matched_brand}}
        )
        updated += 1

print(f"✅ {updated} documents mis à jour avec le champ 'brand' reconnu")
