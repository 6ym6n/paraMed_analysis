import streamlit as st
from pymongo import MongoClient
import pandas as pd

# 🔗 Connexion MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
collection = db["product_match80"]

# 📥 Charger les données
data = list(collection.find({}))
df = pd.DataFrame(data)

# 🧹 Nettoyage
df = df.drop(columns=["_id"], errors="ignore")

# 📋 Liste des pharmacies à détecter dynamiquement
sites = ['parapharma', 'novapara', 'universparadiscount', 'mapara']

# ➕ Ajouter nombre de sites disponibles
def count_sites(row):
    return sum([1 for site in sites if site in row and isinstance(row[site], dict) and 'ma_prix' in row[site]])

df["nb_sites"] = df.apply(count_sites, axis=1)

# 🎛️ Filtre Streamlit
st.sidebar.title("🔎 Filtres")
nb_filter = st.sidebar.selectbox(
    "Afficher les produits disponibles sur combien de sites ?",
    sorted(df["nb_sites"].unique()),
    index=0
)

# 🔍 Filtrer la DataFrame
filtered_df = df[df["nb_sites"] == nb_filter]

# 🧾 Interface
st.title("💊 Comparateur de prix – Produits Parapharmaceutiques")
st.write(f"{len(filtered_df)} produits trouvés sur {nb_filter} site(s)")

for _, row in filtered_df.iterrows():
    st.markdown(f"### 🧴 {row['nom_produit']}")
    table_rows = []

    for site in sites:
        if site in row and isinstance(row[site], dict):
            prix = row[site].get("ma_prix", None)
            name = row[site].get("ma_name", "")
            url = row[site].get("ma_url", "")

            if prix is not None:
                lien = f"[{name}]({url})" if url else name
                table_rows.append((site, f"{prix} DH", lien))

    st.table(pd.DataFrame(table_rows, columns=["Site", "Prix", "Nom / Lien produit"]))
    st.markdown("---")
