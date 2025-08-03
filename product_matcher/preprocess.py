# preprocess.py

import re

def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def create_matching_string(product):
    name = clean_text(product.get("clean_name", ""))
    brand = clean_text(product.get("brand", ""))
    size = clean_text(product.get("size", ""))
    return f"{brand} {name} {size}".strip()
