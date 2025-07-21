import streamlit as st
from analysis.indicators import load_data, get_summary_stats
from components.charts import price_comparison_chart, price_gap_bar_chart

st.set_page_config(page_title="Product Price Intelligence", layout="wide")

st.title("📊 Dashboard Comparatif : Parapharma vs Univers")

# --- Load data ---
df = load_data()

# --- KPI Summary ---
st.subheader("Vue d'ensemble")
stats = get_summary_stats(df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Produits totaux", stats['total_products'])
col2.metric("Prix moyen Parapharma", f"{stats['avg_price_sr']:.2f} MAD")
col3.metric("Prix moyen Univers", f"{stats['avg_price_univers']:.2f} MAD")
col4.metric("Produits en commun", stats['common_products'])

st.divider()

# --- Price gap visual ---
st.subheader("💸 Produits avec les plus grands écarts de prix")
st.plotly_chart(price_gap_bar_chart(df), use_container_width=True)

st.divider()

# --- Price comparison table ---
st.subheader("🆚 Comparateur de prix par produit")
st.dataframe(price_comparison_chart(df), use_container_width=True)
