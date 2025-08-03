"""
Global configuration constants for the paraMed data‑pipeline.

This module centralises parameters that are used across the scraping,
transformation and matching stages.  By keeping all settings in one
place it becomes easy to adjust behaviour without hunting through
multiple scripts.  Values can still be overridden via environment
variables at runtime (see utils/db.py for database settings).
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Embedding and matching configuration
#
# The matching engine relies on sentence embeddings to compare product names.
# You can swap in any model supported by `sentence_transformers`.  The default
# multilingual MiniLM model works well for product names in French and English.

EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"

# Similarity threshold for considering two products a match.  Cosine
# similarity values range between 0 and 1; higher thresholds yield fewer
# matches but higher precision.

SIMILARITY_THRESHOLD: float = 0.90

# ---------------------------------------------------------------------------
# Data sources configuration
#
# These constants define default category lists for the scrapers.  In
# production you may want to fetch categories dynamically or store them in
# a database.  For simplicity the lists here mirror the original JSON
# files found in the legacy repository.


PARAPHARMA_CATEGORIES = [
    {"name": "Visage", "url": "https://parapharma.ma/10-visage"},
    {"name": "Maquillage", "url": "https://parapharma.ma/32-maquillage"},
    {"name": "Corps", "url": "https://parapharma.ma/11-corps"},
    {"name": "Cheveux", "url": "https://parapharma.ma/12-cheveux"},
    {"name": "Bébé et Maman", "url": "https://parapharma.ma/13-bebe-maman"},
    {"name": "Homme", "url": "https://parapharma.ma/15-homme"},
    {"name": "Hygiène", "url": "https://parapharma.ma/16-hygiene"},
    {"name": "Solaire", "url": "https://parapharma.ma/18-solaire"},
    {"name": "Santé", "url": "https://parapharma.ma/19-sante"},
    {"name": "Para_Médical", "url": "https://parapharma.ma/20-para-medical"},
    {"name": "Bio", "url": "https://parapharma.ma/21-bio"},
    {"name": "Promotions", "url": "https://parapharma.ma/promotion"},
]


UNIVERS_CATEGORIES = [
    {"name": "Homme", "url": "https://universparadiscount.ma/492-homme"},
    {"name": "Cheveux", "url": "https://universparadiscount.ma/6-cheveux"},
    {"name": "Visage", "url": "https://universparadiscount.ma/4-visage"},
    {"name": "Maquillage", "url": "https://universparadiscount.ma/237-maquillage-makeup"},
    {"name": "Corps", "url": "https://universparadiscount.ma/5-corps"},
    {"name": "BEBE & MAMAN", "url": "https://universparadiscount.ma/8-bebes-et-mamans"},
    {"name": "DERMOCOSMÉTIQUE", "url": "https://universparadiscount.ma/865-dermocosmetique"},
    {"name": "SANTÉ", "url": "https://universparadiscount.ma/471-sante"},
    {"name": "Produits coreens", "url": "https://universparadiscount.ma/863-produits-coreens"},
]

# ---------------------------------------------------------------------------
# Brand configuration
#
# A curated list of known brands.  The order is important – longer brand
# names should appear before shorter ones so that prefix matching finds
# the most specific brand.  You can extend this list as new brands appear.

KNOWN_BRANDS = [
    "la roche-posay", "la roche posay", "eau thermale avene", "vichy",
    "uriage", "cerave", "bioderma", "nuxe", "avene", "eucerin",
    "ducray", "klorane", "caudalie", "mustela", "filorga", "noreva",
    "topicrem", "isispharma", "embryolisse", "a-derma", "dermagor",
    "svr", "roger gallet", "neutrogena", "l'oreal", "loreal",
    "cetaphil", "bailleul", "biolane", "dermodex", "endocare",
    "lazartigue", "skinceuticals", "apivita", "melvita", "jacomo",
    "avril", "la provençale", "dr hauschka", "elancyl", "galénic",
    "weleda", "bcombio", "lierac", "johnson", "sanoflore", "revox",
    "revlon", "the ordinary", "biosecure", "marilou bio", "gamarde",
    "hydralin", "dermedic", "8882", "photo white"
]

# A blacklist of tokens that should never be considered a brand.  This
# prevents common product terms (e.g. “applicateur”, “brosse”) from being
# misclassified as brands during heuristic extraction.

BRAND_BLACKLIST = {
    'capteur', 'applicateur', 'pistolet', 'chaussettes', 'bracelet', 'brosse',
    'boite', 'bandage', 'coussin', 'coffret', 'sac', 'fauteuil', 'masque',
    'huile', 'tube', 'thermoflash', 'appareil', 'set', 'pack', 'ensemble',
    'accessoire', 'stylo', 'support', 'chaise', 'lampe', 'table', 'tapis',
    'photo', 'oreiller', 'chausson', 'canne', 'bandelette', 'gant', 'collier',
    'calecon', 'slip', 'lit', 'bassin', 'couche', 'biberon', 'biberons',
    'thermometre'
}

# ---------------------------------------------------------------------------
# Paths
#
# Define base paths relative to the package.  You can use these to locate
# resources such as data files.  For example, the scraping modules could
# read category lists from JSON stored beside the code.

PACKAGE_ROOT = Path(__file__).resolve().parent
# Directory for persistent data (e.g. downloads, cached pages)
DATA_DIR = PACKAGE_ROOT / "data"

__all__ = [
    "EMBEDDING_MODEL", "SIMILARITY_THRESHOLD", "PARAPHARMA_CATEGORIES",
    "UNIVERS_CATEGORIES", "KNOWN_BRANDS", "BRAND_BLACKLIST", "PACKAGE_ROOT",
    "DATA_DIR",
]