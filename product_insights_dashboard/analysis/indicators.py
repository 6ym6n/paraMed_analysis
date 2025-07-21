# Fonctions d'analyse (prix moyen, écart, ruptures…)
import pandas as pd
from pymongo import MongoClient
import streamlit as st


@st.cache_data
def load_data():
    client = MongoClient("mongodb://localhost:27017")
    db = client["paraMedProducts"]
    data = list(db["merged"].find({
        "price": {"$ne": None},
        "group_name": {"$exists": True},
        "site": {"$in": ["parapharma.ma", "universparadiscount.ma"]}
    }))
    df = pd.DataFrame(data)
    return df

def get_summary_stats(df):
    total_products = len(df)

    avg_price_sr = df[df["site"] == "parapharma.ma"]["price"].mean()
    avg_price_univers = df[df["site"] == "universparadiscount.ma"]["price"].mean()

    common_products = (
    df.groupby("group_name")["site"]
    .nunique()
    .reset_index()
    .query("site > 1")
    .shape[0]
    )


    return {
        "total_products": total_products,
        "avg_price_sr": avg_price_sr or 0,
        "avg_price_univers": avg_price_univers or 0,
        "common_products": common_products,
    }
