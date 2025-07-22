# post_scraping/scripts/category_mapping.py

category_mapping = {
    # ✅ Visage
    "visage": "Visage",
    "soins visage": "Visage",
    "masques visage": "Visage",
    "gommages visage": "Visage",
    "fonds de teint": "Visage",
    "serums": "Visage",
    "cremes": "Visage",
    "contours yeux": "Visage",
    "peaux matures": "Visage",
    "premieres rides": "Visage",
    "anti imperfections": "Visage",
    "soins contours yeux": "Visage",
    "soins anti imperfections": "Visage",
    "soins hydratants": "Visage",
    "soins eclat et anti taches": "Visage",
    
    # ✅ Corps
    "corps": "Corps",
    "soins corps": "Corps",
    "gommages et exfoliants": "Corps",
    "hydratation corps": "Corps",
    "cellulite et anti vergetures": "Corps",
    "minceur": "Corps",
    "soins mains et pieds": "Corps",
    "soins vergetures": "Corps",

    # ✅ Cheveux
    "cheveux": "Cheveux",
    "shampoings": "Cheveux",
    "apres shampoing": "Cheveux",
    "coloration cheveux": "Cheveux",
    "produits coiffants": "Cheveux",
    "laques cheveux": "Cheveux",
    "gels coiffants": "Cheveux",
    "sprays volume cheveux": "Cheveux",
    "soins des cheveux": "Cheveux",
    
    # ✅ Solaire
    "solaire": "Solaire",
    "cremes solaires": "Solaire",
    "apres soleil": "Solaire",
    "spray solaire": "Solaire",
    "solaires bebes et enfants": "Solaire",
    "huile solaire": "Solaire",
    "gels solaire": "Solaire",

    # ✅ Hygiène
    "hygiene": "Hygiène",
    "hygiene corporelle": "Hygiène",
    "deodorants": "Hygiène",
    "dentifrices": "Hygiène",
    "bains de bouche et haleine fraiche": "Hygiène",
    "brosses a dents adultes": "Hygiène",
    "savon et pain dermatologique": "Hygiène",
    "huiles et cremes minceur": "Hygiène",
    "gels et huiles lavants": "Hygiène",
    "lingettes": "Hygiène",
    
    # ✅ Hygiène intime
    "toilette intime": "Hygiène intime",
    "protections hygieniques et toilette intime": "Hygiène intime",
    "protection hygienique": "Hygiène intime",
    "gynecologie et troubles urinaires": "Hygiène intime",

    # ✅ Maquillage
    "maquillage": "Maquillage",
    "maquillage - makeup": "Maquillage",
    "blush": "Maquillage",
    "fonds de teint": "Maquillage",
    "crayons et mascara": "Maquillage",
    "anti cernes et correcteurs": "Maquillage",
    "levres": "Maquillage",
    "poudres": "Maquillage",
    "teint": "Maquillage",

    # ✅ Compléments / Santé
    "complements alimentaires": "Compléments / Santé",
    "vitamines et formes": "Compléments / Santé",
    "defenses immunitaires": "Compléments / Santé",
    "detox coup faim ventre plat": "Compléments / Santé",
    "circulation sanguine et coeur": "Compléments / Santé",
    "articulations et crampes": "Compléments / Santé",
    "acide hyaluronique": "Compléments / Santé",
    "transit digestion et elimination": "Compléments / Santé",
    "grossesse et maternite": "Compléments / Santé",
    "tisanes": "Compléments / Santé",
    "the tisanes et infusions": "Compléments / Santé",

    # ✅ Bébé & Maternité
    "bébé et maman": "Bébé & Maternité",
    "bebes et mamans": "Bébé & Maternité",
    "repas bebe": "Bébé & Maternité",
    "poussees dentaires bebe": "Bébé & Maternité",
    "tire lait": "Bébé & Maternité",
    "sommeil et detente bebe et enfants": "Bébé & Maternité",
    "bavoirs": "Bébé & Maternité",
    "biberon et goupillon": "Bébé & Maternité",
    "changes bebe": "Bébé & Maternité",
    "langes et couvertures": "Bébé & Maternité",
    "couverts bebe": "Bébé & Maternité",
    "fashion bebe et enfant": "Bébé & Maternité",
    "coussinets d'allaitement et soins": "Bébé & Maternité",
    "apprentissage repas": "Bébé & Maternité",
    "necessaire naissance": "Bébé & Maternité",

    # ✅ Para-médical
    "para_medical": "Para-médical",
    "materiels medicaux": "Para-médical",
    "orthopedie": "Para-médical",
    "thermometres": "Para-médical",
    "tensiometres": "Para-médical",
    "pansements bandages et compresses": "Para-médical",
    "glucometres": "Para-médical",
    "poignet - genou - cheville": "Para-médical",

    # ✅ Produits Bio
    "bio": "Produits Bio",
    "produits bio visage et corps": "Produits Bio",
    "produits cheveux bio": "Produits Bio",
    "cosmetique bio": "Produits Bio",
    "produits hygiene bio": "Produits Bio",
    "bio et naturel": "Produits Bio",
    "alimentation bio et naturel": "Produits Bio",

    # ✅ Promotions
    "promotions": "Promotions",
    "promotions diverses": "Promotions",
    "les bons deals": "Promotions",

    # ✅ Accessoires & outils
    "accessoires": "Accessoires & outils",
    "coffrets": "Accessoires & outils",
    "diffuseurs": "Accessoires & outils",
    "robots cuiseurs sterilisateurs et chauffes biberons": "Accessoires & outils",
    "accessoires de maquillages": "Accessoires & outils",
    "accessoires de sante": "Accessoires & outils",
    "accessoires de soins visage": "Accessoires & outils",
    "accessoires pour cheveux": "Accessoires & outils",

    # ✅ Parfums
    "parfums": "Parfums",

    # 🟡 Par défaut
    "accueil": "Autres",
    "produits du monde": "Autres",
    "produits espagnols": "Autres",
    "produits americains": "Autres",
    "produits coreens": "Autres",
    "produits americains visage et corps": "Autres",
    "produits americains cheveux": "Autres",
    "produits alimentaires bio": "Produits Bio"
}
