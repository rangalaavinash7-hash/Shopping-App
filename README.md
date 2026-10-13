# ShopFinder — Search Once, Compare Everywhere

> **Python Full-Stack Smart Shopping Comparison Website**  
> Built with Python 3, Flask, SQLite3, HTML5, CSS3, Vanilla JavaScript, and Algorithms & Data Structures (ADS).

---

## 1. Project Overview & Features

**ShopFinder** allows shoppers to search for a product once and compare verified deals, prices, ratings, and delivery fees across leading e-commerce platforms in India, including:
- **Amazon**
- **Flipkart**
- **Meesho**
- **Shopsy**
- **Myntra**
- **AJIO**
- **Tata CLiQ**
- **Croma**
- **Reliance Digital**
- **Nykaa**

### Key Features
1. **Modern Purple Gradient UI**: Clean, responsive layout with dark/light mode toggle.
2. **Smart Search with Trie Autocomplete**: Instant search suggestions in $O(L)$ time.
3. **Multi-Platform Comparison Matrix**: Side-by-side comparison table highlighting the **Lowest Verified Total Cost** (`Price + Delivery Charge`).
4. **Budget Level Filtering**:
   - **Low Budget**: ₹0 — ₹500
   - **Medium Budget**: ₹501 — ₹3,000
   - **High Budget**: ₹3,001 — ₹10,000
   - **Premium**: Above ₹10,000
   - Custom price range inputs (Min / Max).
5. **ADS Algorithms Implemented & Tested**:
   - **Linear Search**: $O(N)$ case-insensitive partial match across name, brand, category.
   - **Binary Search**: $O(\log N)$ logarithmic price boundary lookup on pre-sorted arrays.
   - **Merge Sort**: $O(N \log N)$ stable sorting for prices (ascending/descending) and ratings.
   - **Min-Heap (Priority Queue)**: $O(K \log N)$ fast lowest-price offer extraction.
6. **Price History & Chart**: Timestamped observations rendered with smooth trend charts.
7. **User Wishlist & Price Alerts**: Target price alerts with simulation checks.
8. **Admin Dashboard & Pandas Analytics**: Average prices per category, platform volume distributions, and instant CSV/JSON/XML data exports.

---

## 2. Technical Explanations in Telugu (తెలుగు వివరణ)

For beginner-friendly clarity, here are explanations of key algorithmic concepts in simple Telugu along with technical English terms:

| Concept (కాన్సెప్ట్) | English Definition | Telugu Explanation (తెలుగు వివరణ) |
| :--- | :--- | :--- |
| **Trie Data Structure** | A tree-like search structure ordered by word prefixes ($O(L)$). | **ట్రై (Prefix Tree):** యూజర్ సెర్చ్ బార్ లో మొదటి 2 లేదా 3 అక్షరాలు టైప్ చేయగానే, ఆ అక్షరాలతో సరిపోయే వస్తువుల పేర్లను మెరుపు వేగంతో సూచించడానికి (Autocomplete) ఉపయోగపడుతుంది. |
| **Merge Sort** | A divide-and-conquer algorithm that recursively splits arrays ($O(N \log N)$). | **మెర్జ్ సార్ట్:** పెద్ద సంఖ్యలో ఉన్న వస్తువుల ధరలను రెండు సమాన భాగాలుగా విభజించి, క్రమబద్ధీకరించి, తిరిగి కలిపి తక్కువ ధర నుండి ఎక్కువ ధరకు క్రమంలో అమర్చుతుంది. |
| **Min-Heap / Priority Queue** | A complete binary tree where the root is always the minimum item ($O(K \log N)$). | **మిన్-హీప్ (కనిష్ట ధర ఎంపిక):** మొత్తం వేల కొద్దీ ఆఫర్లను సార్ట్ చేయనవసరం లేకుండా, అత్యల్ప ధర కలిగిన టాప్ 5 ఆఫర్లను అతి తక్కువ సమయంలో ఎంచుకుంటుంది. |
| **Verified Total Price** | `Current Price + Delivery Charge`. | **వెరిఫైడ్ టోటల్ ప్రైస్:** కేవలం వస్తువు ధర మాత్రమే కాకుండా డెలివరీ ఛార్జీలను కూడా కలిపి కస్టమర్ చెల్లించాల్సిన అసలైన మొత్తాన్ని లెక్కిస్తుంది. |
| **Adapter Pattern** | Structural design pattern for modular platform integrations. | **అడాప్టర్ ప్యాటర్న్:** కొత్త షాపింగ్ ప్లాట్‌ఫారమ్‌లు వచ్చినప్పుడు యాప్ కోడ్ మొత్తం మార్చకుండా సులభంగా కొత్త ప్లాట్‌ఫారమ్‌ను జోడించడానికి సహాయపడుతుంది. |

---

## 3. Demonstration Data vs. Real Platform Integration

- **Demonstration Mode (Active & Fully Operational)**:
  ShopFinder ships with pre-seeded demonstration data across all 19 categories and 10 platforms stored in SQLite (`database/shopfinder.db`). It runs completely offline without needing third-party API keys.
- **Real Platform Integration (Future Extension)**:
  Real-time integration with Amazon PA-API 5.0, Flipkart Affiliate API, or Croma feeds requires official developer accounts, associate tags, and partner agreements. The architecture in `integrations/base_adapter.py` provides clean blueprint adapters ready for API keys whenever acquired.

---

## 4. Complete Project Directory Structure

```text
ShopFinder/
├── app.py                      # Flask main server & REST API
├── database.py                 # SQLite initialization & demo seeding script
├── models.py                   # OOP classes: Product, ShoppingPlatform, ProductOffer, PriceTracker
├── config.py                   # Configuration, budget tiers, and platform lists
├── requirements.txt            # Python dependencies (Flask, pandas, werkzeug)
├── README.md                   # Complete documentation & guides
├── .env.example                # Sample environment configuration
├── .gitignore                  # Git ignore rules
├── algorithms/
│   ├── __init__.py
│   ├── search.py               # Linear Search, Binary Search, and Trie Autocomplete
│   ├── sorting.py              # Merge Sort (Asc/Desc) and benchmarks
│   └── recommendations.py      # Min-Heap and multi-criteria value scorer
├── services/
│   ├── __init__.py
│   ├── product_service.py      # Product business logic, filters, and Trie integration
│   ├── comparison_service.py   # Side-by-side matrices and lowest price calculations
│   └── platform_service.py     # Shopping platform managers and adapters
├── integrations/
│   ├── __init__.py
│   └── base_adapter.py         # Extensible adapter blueprints
├── database/
│   └── shopfinder.db           # SQLite database
├── templates/
│   ├── base.html               # Master layout with purple theme and navbar
│   ├── index.html              # Hero section, platforms, budget tiers, calculator
│   ├── products.html           # Full catalog with reactive sidebar filters
│   ├── compare.html            # Side-by-side comparison & historical price chart
│   ├── wishlist.html           # User saved products
│   ├── history.html            # Search queries & activity log
│   ├── login.html              # Sign in with instant demo user buttons
│   ├── register.html           # Account registration
│   ├── admin.html              # Admin CRUD and Pandas data science analytics
│   ├── about.html              # Architecture & syllabus details
│   └── contact.html            # Contact support form
├── static/
│   ├── css/
│   │   └── style.css           # Master CSS design system with Dark/Light modes
│   ├── js/
│   │   ├── app.js              # Theme switcher, toasts, compare tray
│   │   ├── search.js           # Live Trie autocomplete and catalog filtering
│   │   ├── compare.js          # Comparison matrix and Chart.js rendering
│   │   └── wishlist.js         # Wishlist management
│   └── images/
└── tests/
    ├── __init__.py
    ├── test_search.py          # Unit tests for Linear, Binary, and Trie search
    ├── test_sorting.py         # Unit tests for Merge Sort and benchmarks
    └── test_api.py             # Integration tests for all Flask API endpoints
```

---

## 5. Windows & VS Code Step-by-Step Execution Guide

### Step 1: Open VS Code and Terminal
1. Open **Visual Studio Code**.
2. Press `Ctrl + ~` (or go to **Terminal** -> **New Terminal**) to open PowerShell.
3. Navigate to the `ShopFinder` project folder:
   ```powershell
   cd "c:\Users\DIVYA SURYA\OneDrive\Desktop\ShopFinder"
   ```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
*(If PowerShell displays an execution policy warning, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and then run the activation script again).*

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Initialize SQLite Database and Seed Data
```powershell
python database.py
```
*Expected output: `Database schema successfully initialized. Demonstration data seeded successfully across all categories and platforms!`*

### Step 5: Run Automated Unit & API Tests
```powershell
python -m unittest discover tests
```
*Expected output: `Ran 21 tests in 0.480s — OK`*

### Step 6: Start the Flask Development Server
```powershell
python app.py
```
*Expected output:*
```text
============================================================
 ShopFinder Server Running on http://127.0.0.1:5000 
============================================================
 * Running on http://127.0.0.1:5000
```

### Step 7: Open in Web Browser
Open Google Chrome, Edge, or Opera and visit:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 6. Pre-Configured Demo Accounts for Testing

| Role | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Regular Shopper** | `shopper` | `shop123` | Test wishlist, search history, price alerts |
| **Administrator** | `admin` | `admin123` | Access Admin panel (`/admin`), product CRUD, Pandas analytics |

*Tip: On the `/login` page, you can click **"Shopper (shopper)"** or **"Admin (admin)"** to instantly fill credentials with one click!*

---

## 7. Verification Checklist

- [x] **Database Initialized**: SQLite tables created with indexes in `database/shopfinder.db`.
- [x] **19 Product Categories**: Fully represented with demonstration offers across all budget tiers.
- [x] **10 Shopping Platforms**: Amazon, Flipkart, Meesho, Shopsy, Myntra, AJIO, Tata CLiQ, Croma, Reliance Digital, Nykaa.
- [x] **ADS Search Algorithms**: Linear Search, Binary Search, and Trie autocomplete suggestions verified.
- [x] **ADS Merge Sort**: Ascending and descending price ordering tested against Python `sorted()`.
- [x] **Min-Heap Priority Queue**: Lowest total verified cost (`Price + Delivery`) highlighting verified.
- [x] **Side-by-Side Comparison**: Side-by-side matrices and difference highlighting functioning.
- [x] **Historical Price Chart**: Timestamped price records rendered with Chart.js.
- [x] **Dark / Light Mode**: Seamless toggling with instant local preference storage.
- [x] **Admin & Data Science**: Pandas DataFrame analytical summaries, CSV, JSON, and XML exports.
- [x] **21 Automated Tests Passing**: All tests in `tests/` pass with 100% success rate.
