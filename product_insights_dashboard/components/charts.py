# Fonctions de visualisation Plotly/Matplotlib
import pandas as pd
import plotly.express as px


def price_comparison_chart(df):
    # Produits présents sur les 2 sites
    pivot = df.pivot_table(index="group_name", columns="site", values="price", aggfunc="first")
    pivot = pivot.dropna().reset_index()
    pivot["difference"] = (pivot["parapharma.ma"] - pivot["universparadiscount.ma"]).abs()

    # Affichage pour Streamlit
    pivot = pivot.sort_values("difference", ascending=False)
    pivot = pivot.rename(columns={
        "parapharma.ma": "Prix Parapharma",
        "universparadiscount.ma": "Prix Univers",
        "difference": "Écart de prix"
    })
    return pivot[["group_name", "Prix Parapharma", "Prix Univers", "Écart de prix"]]


def price_gap_bar_chart(df):
    pivot = df.pivot_table(index="group_name", columns="site", values="price", aggfunc="first")
    pivot = pivot.dropna().reset_index()
    pivot["price_gap"] = (pivot["parapharma.ma"] - pivot["universparadiscount.ma"]).abs()

    top_diff = pivot.sort_values("price_gap", ascending=False).head(15)

    fig = px.bar(
        top_diff,
        x="price_gap",
        y="group_name",
        orientation="h",
        title="Top 15 écarts de prix entre les deux sites",
        labels={"group_name": "Produit", "price_gap": "Écart de prix (MAD)"}
    )
    fig.update_layout(yaxis_title="Produit", xaxis_title="Écart de prix (MAD)", height=600)
    return fig
