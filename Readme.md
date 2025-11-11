# 🔐 Encrypted Database Search for E-Commerce Systems

## 📘 Overview

This project demonstrates **privacy-preserving search** in an e-commerce system where all product data is stored **encrypted** in the database.  
It allows users to perform search operations **without decrypting the entire database** — ensuring **data confidentiality** while maintaining search functionality.

The system supports two search modes:

1. **Option 1 — Encrypted Keyword Index Search**  
   Enables searching encrypted product records by keywords (e.g., *laptop*, *shoes*, *headphones*).  
   Each keyword is deterministically tokenized using a cryptographic HMAC, and an encrypted inverted index maps tokens to product IDs.

2. **Option 2 — Deterministic Field Equality Search**  
   Enables exact-match searches on specific fields (e.g., search by exact *Product Name*).  
   Uses deterministic encryption (via HMAC) to compare encrypted field tokens directly without decryption.

All product data is encrypted using **AES-GCM**, and deterministic tokens are derived using **HMAC-SHA256**.  
The project also includes a simple **Flask-based backend**, **SQLite** database, and a **minimal frontend** for interacting with the system.

---

## 🧠 Conceptual Flow

1. **Product Insertion**
   - When a new product is added:
     - The entire product record is encrypted using **AES-GCM**.
     - Keywords from name/description/category are tokenized (HMAC-based) and stored in an **encrypted keyword index**.
     - A deterministic token for the product name is generated for equality-based searches.
   - Encrypted record and tokens are stored in the database.

2. **Keyword Search (Option 1)**
   - User enters a keyword (e.g., “laptop”).
   - The system computes the same deterministic token (HMAC of keyword).
   - It retrieves all encrypted product IDs associated with that token, decrypts them, and shows results.

3. **Exact Name Search (Option 2)**
   - User enters the exact product name.
   - System computes its deterministic token and checks for equality in the database.
   - Matching encrypted records are decrypted and displayed.

4. **Decryption**
   - All decryption happens **server-side** (for demo purposes) before sending results to the frontend.

---

## 🧩 Project Structure

```
encrypted_search_app/
├── backend.py              # Flask backend (API + encryption logic)
├── encrypted_search.db      # SQLite database (encrypted records + indexes)
├── keys.json               # Demo cryptographic keys (Base64 encoded)
├── templates/
│   └── index.html          # Frontend HTML UI
└── static/
    └── app.js              # Frontend JavaScript (API calls)
```

---

## ⚙️ Tech Stack

| Component | Technology Used |
|------------|----------------|
| Backend | Python Flask |
| Encryption | AES-GCM (Confidentiality) + HMAC-SHA256 (Deterministic Tokens) |
| Database | SQLite |
| Frontend | HTML, JavaScript (Fetch API) |
| Dataset | Dummy product dataset (10 sample items) |

---

## 🚀 How to Run

### 1️⃣ Prerequisites
Make sure you have Python 3.9+ installed.

Install dependencies:
```bash
pip install flask cryptography
```

### 2️⃣ Run the Server
```bash
cd encrypted_search_app
python backend.py
```

The server will start on:
```
http://127.0.0.1:5000
```

### 3️⃣ Use the Web Interface
- Open your browser at the address above.
- Use the **Keyword Search** form to search for items (e.g. `laptop`, `shoes`, `headphones`).
- Use the **Exact Name Search** form to match full product names (e.g. `UltraFast Laptop 13"`).
- Use the **Add Product** form to insert new encrypted products.

---

## 🧪 Example Queries

| Type | Input | Result |
|------|--------|--------|
| Keyword Search | `laptop` | UltraFast Laptop 13" |
| Keyword Search | `shoes` | Running Shoes - SpeedX, Trail Running Shoes |
| Name Search | `Noise-Cancelling Headphones` | One exact match |

---

## 🔒 Security Notes

- **AES-GCM** provides confidentiality and integrity for all stored product data.
- **HMAC-SHA256** deterministic tokens are used for searching (leak equality patterns only).
- Keys are stored in `keys.json` for demo simplicity.  
  ⚠️ In a real system, keys must be managed securely (e.g., using an HSM or key vault).
- The backend performs decryption — a stronger system could shift decryption client-side.
- This demo omits advanced protections like **access-pattern hiding** (SSE/ORAM).

---

## 🧱 Future Enhancements

- Add **Symmetric Searchable Encryption (SSE)** for stronger privacy.
- Implement **range queries** using Order-Preserving or Order-Revealing Encryption.
- Support **user authentication** for access control.
- Move **decryption to the client-side** using WebCrypto API.
- Add **Dockerfile** for containerized deployment.

