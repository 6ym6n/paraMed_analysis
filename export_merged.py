#!/usr/bin/env python3
"""
Export MongoDB merged collection to CSV & JSONL for Colab fine-tuning.
"""

import csv, json, unicodedata, re, os
from pymongo import MongoClient
import pandas as pd

### ---------- PARAMS ----------
MONGO_URI      = "mongodb://localhost:27017"
DB_NAME        = "paraMedProducts"
COLL_NAME      = "merged"              # ← collection fusionnée
OUT_CSV        = "products_merged.csv"
OUT_JSONL      = "products_merged.jsonl"
FIELDS_TO_KEEP = ["_id", "brand", "name", "clean_name",
                  "category", "qty", "price", "site", "product_url"]
# --------------------------------

def slugify(txt: str) -> str:
    if not txt:
        return ""
    txt = unicodedata.normalize("NFD", txt).encode("ascii", "ignore").decode()
    txt = re.sub(r"[^\w\s-]", "", txt).strip().lower()
    return re.sub(r"[-\s]+", "-", txt)

def main():
    client = MongoClient(MONGO_URI)
    coll   = client[DB_NAME][COLL_NAME]

    cursor = coll.find({}, {f: 1 for f in FIELDS_TO_KEEP})
    records = list(cursor)               # → mémoire OK si < 1-2 M lignes ; sinon streamer

    # NORMALISATIONS légères (exemple)
    for r in records:
        r["brand"] = (r.get("brand") or "").strip().title()
        r["slug"]  = slugify(r.get("clean_name") or r.get("name"))

    # ---- CSV ----
    df = pd.DataFrame(records)
    df.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_ALL)
    print(f"✅ CSV exporté : {OUT_CSV} ({len(df):,} lignes)")

    # ---- JSON lines ----
    with open(OUT_JSONL, "w", encoding="utf-8") as f:
        for rec in records:
            # Mongo’s ObjectId n’est pas JSON-serialisable → cast en str
            rec["_id"] = str(rec["_id"])
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"✅ JSONL exporté : {OUT_JSONL}")

if __name__ == "__main__":
    main()
