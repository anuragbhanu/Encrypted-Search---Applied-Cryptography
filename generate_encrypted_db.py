"""
generate_encrypted_db.py
------------------------
Creates a sample encrypted SQLite database for the
'Encrypted Database Search for E-Commerce Systems' project.

Implements:
 - AES-GCM encryption for full product records
 - HMAC-SHA256 deterministic tokens for keyword & name search
 - Two tables: products (encrypted records) and keyword_index
"""

import json
import base64
import sqlite3
import hashlib, hmac, secrets, re
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# -----------------------------
# 1️⃣  Dummy product dataset
# -----------------------------
products = [
    {"id": 1, "name": "UltraFast Laptop 13\"", "description": "Lightweight laptop with 16GB RAM", "category": "Electronics", "price": 999},
    {"id": 2, "name": "Noise-Cancelling Headphones", "description": "Over-ear headphones, Bluetooth", "category": "Electronics", "price": 199},
    {"id": 3, "name": "Running Shoes - SpeedX", "description": "Comfortable running shoes for daily training", "category": "Footwear", "price": 120},
    {"id": 4, "name": "Smartphone Pro Max", "description": "6.7 inch display, 256GB storage", "category": "Electronics", "price": 1099},
    {"id": 5, "name": "Leather Wallet", "description": "Genuine leather, slim design", "category": "Accessories", "price": 49},
    {"id": 6, "name": "4K Monitor 27 inch", "description": "High-resolution display for creators", "category": "Electronics", "price": 349},
    {"id": 7, "name": "Yoga Mat", "description": "Non-slip yoga mat, 6mm thickness", "category": "Fitness", "price": 35},
    {"id": 8, "name": "Trail Running Shoes", "description": "Rugged outsole for trails", "category": "Footwear", "price": 140},
    {"id": 9, "name": "Wireless Mouse", "description": "Ergonomic mouse with long battery life", "category": "Electronics", "price": 29},
    {"id": 10, "name": "Classic T-Shirt", "description": "Cotton t-shirt, unisex fit", "category": "Apparel", "price": 19}
]

# -----------------------------
# 2️⃣  Key generation
# -----------------------------
DATA_KEY = secrets.token_bytes(32)   # AES-GCM key for record encryption
SEARCH_KEY = secrets.token_bytes(32) # HMAC key for keyword search
DET_KEY = secrets.token_bytes(32)    # HMAC key for deterministic equality search

def save_keys():
    with open("keys.json", "w") as f:
        json.dump({
            "DATA_KEY": base64.b64encode(DATA_KEY).decode(),
            "SEARCH_KEY": base64.b64encode(SEARCH_KEY).decode(),
            "DET_KEY": base64.b64encode(DET_KEY).decode()
        }, f, indent=2)
    print("✅ Keys saved to keys.json")

# -----------------------------
# 3️⃣  Crypto helper functions
# -----------------------------
def aesgcm_encrypt(key, plaintext: bytes) -> str:
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)
    ct = aesgcm.encrypt(nonce, plaintext, None)
    return base64.b64encode(nonce + ct).decode()

def aesgcm_decrypt(key, token_b64: str) -> bytes:
    data = base64.b64decode(token_b64)
    nonce, ct = data[:12], data[12:]
    return AESGCM(key).decrypt(nonce, ct, None)

def det_token(key, message: str) -> str:
    return hmac.new(key, message.lower().encode(), hashlib.sha256).hexdigest()

# -----------------------------
# 4️⃣  Build keyword index
# -----------------------------
def extract_keywords(text):
    words = re.findall(r"[A-Za-z0-9']{3,}", text.lower())
    return set(words)

keyword_index = {}  # token -> list of encrypted docIDs

# -----------------------------
# 5️⃣  Create SQLite DB
# -----------------------------
conn = sqlite3.connect("encrypted_search.db")
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS products")
cur.execute("DROP TABLE IF EXISTS keyword_index")

cur.execute("""
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    enc_record TEXT,
    det_name_token TEXT
)
""")

cur.execute("""
CREATE TABLE keyword_index (
    token TEXT,
    enc_docid TEXT
)
""")

# -----------------------------
# 6️⃣  Encrypt and insert data
# -----------------------------
for p in products:
    # Encrypt full record
    plaintext = json.dumps(p).encode()
    enc_record = aesgcm_encrypt(DATA_KEY, plaintext)

    # Deterministic name token (Option 2)
    det_name_token = det_token(DET_KEY, p["name"])

    # Insert product
    cur.execute("INSERT INTO products (id, enc_record, det_name_token) VALUES (?, ?, ?)",
                (p["id"], enc_record, det_name_token))

    # Extract and index keywords (Option 1)
    text = f"{p['name']} {p['description']} {p['category']}"
    for kw in extract_keywords(text):
        token = det_token(SEARCH_KEY, kw)
        enc_docid = aesgcm_encrypt(DATA_KEY, str(p["id"]).encode())
        cur.execute("INSERT INTO keyword_index (token, enc_docid) VALUES (?, ?)", (token, enc_docid))

conn.commit()
conn.close()
save_keys()
print("✅ Encrypted database generated: encrypted_search.db")
print("✅ Keyword index built for Option 1, deterministic name index built for Option 2")
