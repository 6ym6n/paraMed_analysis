# Install required packages

# Import libraries
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Upload your exported MongoDB product CSV

# Load the dataset
df = pd.read_csv("merged.csv")
df['size'] = df['size'].fillna('')
df['brand'] = df['brand'].fillna('')
df['clean_name'] = df['clean_name'].fillna('')
df['price'] = df['price'].fillna(0)

# Load sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Compute embeddings for clean_name
df['embedding'] = model.encode(df['clean_name'].tolist(), show_progress_bar=True).tolist()

# Split data by site
df_a = df[df['site'] == 'parapharma.ma'].reset_index(drop=True)
df_b = df[df['site'] == 'universparadiscount.ma'].reset_index(drop=True)

# Compute cosine similarity between all product pairs (brute-force)
emb_a = np.vstack(df_a['embedding'])
emb_b = np.vstack(df_b['embedding'])
similarities = cosine_similarity(emb_a, emb_b)

# For each product in df_a, find best match in df_b
matches = []
for i, sim_row in enumerate(similarities):
    j = np.argmax(sim_row)
    sim_score = sim_row[j]

    product_a = df_a.iloc[i]
    product_b = df_b.iloc[j]

    # Compute price gap percentage
    max_price = max(product_a['price'], product_b['price'])
    if max_price == 0:
        price_gap_pct = 1  # fallback if prices are zero
    else:
        price_gap_pct = abs(product_a['price'] - product_b['price']) / max_price

    # Match conditions:
    # Brand match if both present
    if product_a['brand'] and product_b['brand']:
        if product_a['brand'].lower() != product_b['brand'].lower():
            continue

    # Size match if both present
    if product_a['size'] and product_b['size']:
        if product_a['size'].lower() != product_b['size'].lower():
            continue

    # Price gap filter
    if price_gap_pct > 0.20:
        continue

    # Save match
    matches.append({
        'brand': product_a['brand'],
        'name_a': product_a['clean_name'],
        'price_a': product_a['price'],
        'url_a': product_a['product_url'],
        'name_b': product_b['clean_name'],
        'price_b': product_b['price'],
        'url_b': product_b['product_url'],
        'sim_score': round(sim_score, 4),
        'price_gap_pct': round(price_gap_pct, 4),
    })

# Convert matches to DataFrame
matched_df = pd.DataFrame(matches)

print(f"✅ Total matched products: {len(matched_df)}")

# Preview and export to CSV
matched_df.head()
matched_df.to_csv("matched_products.csv", index=False)
