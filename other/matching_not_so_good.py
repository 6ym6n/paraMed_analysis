# 🛠️ Installer les dépendances

# 📚 Importer les modules
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import networkx as nx

# 📂 Charger les données
df = pd.read_csv("/products_merged.csv")
df['clean_name'] = df['clean_name'].fillna("").astype(str)

# ⚙️ Étape 1 – Embedding des noms
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(df['clean_name'].tolist(), convert_to_tensor=False, show_progress_bar=True)
embeddings = np.array(embeddings).astype("float32")
faiss.normalize_L2(embeddings)

# 🔍 Étape 2 – FAISS similarity search
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)
k = 5
distances, indices = index.search(embeddings, k)

# 🔗 Étape 3 – Créer un graphe de similarité
G = nx.Graph()
threshold = 0.80

for i in range(len(indices)):
    G.add_node(i)
    for j, score in zip(indices[i][1:], distances[i][1:]):
        if score >= threshold:
            G.add_edge(i, j)

# 🧩 Étape 4 – Trouver les clusters de produits similaires
clusters = list(nx.connected_components(G))

# 🧾 Étape 5 – Regrouper infos par site pour chaque cluster
records = []
for cluster in clusters:
    cluster = list(cluster)
    nom_canonique = df.iloc[cluster[0]]['clean_name']

    prix_par_site = {}
    name_par_site = {}
    url_par_site = {}

    for i in cluster:
        row = df.iloc[i]
        site = row['site']
        prix = row['price']
        name = row['clean_name']
        url = row['product_url'] if pd.notnull(row['product_url']) else ""

        prix_par_site[f"{site}_prix"] = prix
        name_par_site[f"{site}_name"] = name
        url_par_site[f"{site}_url"] = url

    record = {'nom_produit': nom_canonique}
    record.update(prix_par_site)
    record.update(name_par_site)
    record.update(url_par_site)

    if prix_par_site:
        prix_vals = [v for v in prix_par_site.values() if isinstance(v, (int, float))]
        if len(prix_vals) > 1:
            record['écart_max_min'] = max(prix_vals) - min(prix_vals)
        else:
            record['écart_max_min'] = 0
    else:
        record['écart_max_min'] = None

    records.append(record)

# 📊 Étape 6 – Résultat final
final_df = pd.DataFrame(records)

# 📦 Étape 7 – Sauvegarde
final_df.to_csv("produits_comparés80V4.csv", index=False)
print(f"✅ Fichier 'produits_comparés80.csv' généré avec {len(final_df)} lignes")
