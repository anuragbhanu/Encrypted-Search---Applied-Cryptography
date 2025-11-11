#!/usr/bin/env python3
"""Flask backend for Encrypted Search demo (Options 1 & 2)
Run: python backend.py
Requires: pip install flask cryptography
"""
import os, json, base64, sqlite3, hmac, hashlib
from flask import Flask, request, render_template, jsonify
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Load keys (demo file)
with open(os.path.join(os.path.dirname(__file__), "keys.json"), "r") as f:
    keys = json.load(f)
DATA_KEY = base64.b64decode(keys["DATA_KEY"])
DET_KEY = base64.b64decode(keys["DET_KEY"])
SEARCH_KEY = base64.b64decode(keys["SEARCH_KEY"])

DB_PATH_CAND1 = os.path.join(os.path.dirname(__file__), "encrypted_search.db")
DB_PATH_CAND2 = os.path.join(os.path.dirname(__file__), "..", "encrypted_search.db")
DB_PATH = DB_PATH_CAND1 if os.path.exists(DB_PATH_CAND1) else DB_PATH_CAND2

app = Flask(__name__, template_folder="templates", static_folder="static")

def aesgcm_decrypt(key: bytes, token_b64: str) -> bytes:
    data = base64.b64decode(token_b64.encode())
    nonce, ct = data[:12], data[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, None)

def det_token(key: bytes, message: str) -> str:
    return hmac.new(key, message.encode('utf-8'), hashlib.sha256).hexdigest()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search/keyword", methods=["POST"])
def search_keyword():
    # Option 1: Encrypted Keyword Index search
    data = request.get_json()
    if not data or "keyword" not in data:
        return jsonify({"error":"missing keyword"}), 400
    keyword = data["keyword"].lower()
    token = det_token(SEARCH_KEY, keyword)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT postings FROM keyword_index WHERE token = ?", (token,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"results": []})
    enc_postings = json.loads(row[0])
    docids = []
    for encid in enc_postings:
        try:
            docid = int(aesgcm_decrypt(DATA_KEY, encid).decode())
            docids.append(docid)
        except Exception:
            pass
    # decrypt full records
    results = []
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for did in docids:
        cur.execute("SELECT enc_record FROM products WHERE id = ?", (did,))
        r = cur.fetchone()
        if not r:
            continue
        try:
            rec = json.loads(aesgcm_decrypt(DATA_KEY, r[0]).decode())
            results.append(rec)
        except Exception:
            pass
    conn.close()
    return jsonify({"results": results})

@app.route("/search/name", methods=["POST"])
def search_name():
    # Option 2: Deterministic equality search on name
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error":"missing name"}), 400
    name = data["name"]  # exact name expected
    token = det_token(DET_KEY, name)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT enc_record FROM products WHERE det_name_token = ?", (token,))
    rows = cur.fetchall()
    conn.close()
    results = []
    for r in rows:
        try:
            results.append(json.loads(aesgcm_decrypt(DATA_KEY, r[0]).decode()))
        except Exception:
            pass
    return jsonify({"results": results})

@app.route("/add", methods=["POST"])
def add_product():
    # Add a new product (plaintext JSON fields: name, description, category, price)
    data = request.get_json()
    if not data:
        return jsonify({"error":"missing product data"}), 400
    for fld in ("name","description","category","price"):
        if fld not in data:
            return jsonify({"error":f"missing field: {fld}"}), 400
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT MAX(id) FROM products")
    row = cur.fetchone()
    nid = (row[0] or 0) + 1
    product = { "id": nid, "name": data["name"], "description": data["description"], "category": data["category"], "price": data["price"] }
    # encrypt full record
    aesgcm = AESGCM(DATA_KEY)
    import secrets as _secrets, base64 as _base64, json as _json
    n = _secrets.token_bytes(12)
    ct = aesgcm.encrypt(n, _json.dumps(product).encode('utf-8'), None)
    enc_blob = _base64.b64encode(n + ct).decode()
    det = hmac.new(DET_KEY, product["name"].encode('utf-8'), hashlib.sha256).hexdigest()
    cur.execute("INSERT INTO products (id, enc_record, det_name_token) VALUES (?, ?, ?)", (nid, enc_blob, det))
    conn.commit()
    # update keyword index
    import re, json as _json2, hmac as _hmac, hashlib as _hashlib, base64 as _base64b
    def extract_keywords(text):
        return set(re.findall(r"[A-Za-z0-9']{3,}", text.lower()))
    kws = extract_keywords(product["name"] + " " + product["description"] + " " + product["category"])
    for kw in kws:
        token_kw = hmac.new(SEARCH_KEY, kw.encode('utf-8'), hashlib.sha256).hexdigest()
        cur.execute("SELECT postings FROM keyword_index WHERE token = ?", (token_kw,))
        r = cur.fetchone()
        # encrypt docid with AES-GCM for consistency (reuse DATA_KEY)
        n2 = _secrets.token_bytes(12)
        enc_id = _base64b.b64encode(n2 + AESGCM(DATA_KEY).encrypt(n2, str(nid).encode(), None)).decode()
        if r:
            postings = json.loads(r[0])
            postings.append(enc_id)
            cur.execute("UPDATE keyword_index SET postings = ? WHERE token = ?", (json.dumps(postings), token_kw))
        else:
            cur.execute("INSERT INTO keyword_index (token, postings) VALUES (?, ?)", (token_kw, json.dumps([enc_id])))
    conn.commit()
    conn.close()
    return jsonify({"ok":True, "id": nid})

if __name__ == "__main__":
    print("Starting Flask app on http://127.0.0.1:5000")
    app.run(debug=True)
