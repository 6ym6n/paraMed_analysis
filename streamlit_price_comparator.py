import streamlit as st
from pymongo import MongoClient
import pandas as pd

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["paraMedProducts"]
collection = db["matched_products"]

st.title("💊 Comparateur de prix - Parapharma vs Univers")

# Chargement des données depuis MongoDB
@st.cache_data
def load_data():
    data = list(collection.find())
    return pd.DataFrame(data)

df = load_data()

if df.empty:
    st.warning("Aucune correspondance trouvée dans la base de données.")
    st.stop()

# Conversion écart pour le filtre
df["écart_max_min"] = df["écart_max_min"].astype(float)

# Filtrage interactif
max_ecart = st.slider("Filtrer par écart maximum (MAD)", 0, int(df["écart_max_min"].max()), 50)
df_filtered = df[df["écart_max_min"] <= max_ecart]

# Affichage tableau
st.write(f"🔍 {len(df_filtered)} correspondances trouvées avec un écart ≤ {max_ecart} MAD")

for _, row in df_filtered.iterrows():
    st.markdown("---")
    st.markdown(f"### 🧴 {row['nom_produit'].title()}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Parapharma**")
        st.markdown(f"[{row['parapharma']['ma_name']}]({row['parapharma']['ma_url']})")
        st.markdown(f"💰 Prix : {row['parapharma']['ma_prix']} MAD")

    with col2:
        st.markdown("**Univers**")
        st.markdown(f"[{row['universparadiscount']['ma_name']}]({row['universparadiscount']['ma_url']})")
        st.markdown(f"💰 Prix : {row['universparadiscount']['ma_prix']} MAD")

    st.markdown(f"➡️ **Écart** : {row['écart_max_min']} MAD")
