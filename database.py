"""
ShopFinder Database Module
Handles SQLite schema creation, database connection, and rich demonstration seeding.
Includes tables: users, platforms, categories, products, product_offers,
price_history, wishlist, search_history, and price_alerts.
"""

import os
import sqlite3
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash
from config import Config


def get_db_connection():
    """
    Returns an SQLite connection with Row factory enabled for dictionary-like access.
    """
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """
    Initializes database tables, indexes, and initial constraints.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)

    # 2. Platforms Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS platforms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform_name TEXT UNIQUE NOT NULL,
        website_url TEXT NOT NULL,
        logo_icon TEXT NOT NULL,
        integration_type TEXT DEFAULT 'DEMO',
        is_active INTEGER DEFAULT 1
    )
    """)

    # 3. Categories Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT UNIQUE NOT NULL,
        icon TEXT DEFAULT 'bi-tag'
    )
    """)

    # 4. Products Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        brand TEXT NOT NULL,
        model TEXT DEFAULT '',
        category_id INTEGER NOT NULL,
        description TEXT DEFAULT '',
        image_url TEXT NOT NULL,
        specifications TEXT DEFAULT '',
        FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
    )
    """)

    # 5. Product Offers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS product_offers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        platform_id INTEGER NOT NULL,
        current_price REAL NOT NULL,
        original_price REAL NOT NULL,
        rating REAL DEFAULT 0.0,
        review_count INTEGER DEFAULT 0,
        product_url TEXT NOT NULL,
        delivery_charge REAL DEFAULT 0.0,
        availability TEXT DEFAULT 'In Stock',
        data_source TEXT DEFAULT 'DEMONSTRATION',
        last_updated TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
        FOREIGN KEY (platform_id) REFERENCES platforms (id) ON DELETE CASCADE
    )
    """)

    # 6. Price History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        offer_id INTEGER NOT NULL,
        recorded_price REAL NOT NULL,
        recorded_at TEXT NOT NULL,
        FOREIGN KEY (offer_id) REFERENCES product_offers (id) ON DELETE CASCADE
    )
    """)

    # 7. Wishlist Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        UNIQUE(user_id, product_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
    )
    """)

    # 8. Search History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        search_query TEXT NOT NULL,
        searched_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    # 9. Price Alerts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        offer_id INTEGER NOT NULL,
        target_price REAL NOT NULL,
        is_active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL,
        triggered_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (offer_id) REFERENCES product_offers (id) ON DELETE CASCADE
    )
    """)

    # Create Indexes for Search and Sorting Performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_name ON products(product_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_offers_product ON product_offers(product_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_offers_platform ON product_offers(platform_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_offers_price ON product_offers(current_price)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_offer ON price_history(offer_id)")

    conn.commit()
    conn.close()
    print("Database schema successfully initialized.")


def seed_data():
    """
    Populates database with realistic demonstration data for all categories,
    multiple shopping platforms, user accounts, and historical price records.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] > 0:
        print("Database already contains data. Skipping seeding.")
        conn.close()
        return

    print("Seeding demonstration data...")

    # 1. Seed Users (Demo Admin and Normal Shopper)
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    admin_hash = generate_password_hash("admin123")
    shopper_hash = generate_password_hash("shop123")

    cursor.execute("""
    INSERT INTO users (username, email, password_hash, is_admin, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, ("admin", "admin@shopfinder.in", admin_hash, 1, now_str))

    cursor.execute("""
    INSERT INTO users (username, email, password_hash, is_admin, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, ("shopper", "shopper@example.com", shopper_hash, 0, now_str))

    # 2. Seed Platforms
    platform_map = {}
    for p in Config.PLATFORMS:
        cursor.execute("""
        INSERT INTO platforms (platform_name, website_url, logo_icon, integration_type, is_active)
        VALUES (?, ?, ?, 'DEMO', 1)
        """, (p["name"], p["url"], p["logo"]))
        platform_map[p["name"]] = cursor.lastrowid

    # 3. Seed Categories with appropriate icons
    cat_icons = {
        "Mobiles": "bi-phone",
        "Laptops": "bi-laptop",
        "Electronics": "bi-cpu",
        "Bluetooth Earbuds": "bi-earbuds",
        "Headphones": "bi-headphones",
        "Men’s Clothing": "bi-person",
        "Women’s Clothing": "bi-person-heart",
        "Shoes": "bi-boot",
        "Watches": "bi-smartwatch",
        "Bags": "bi-backpack",
        "Beauty Products": "bi-stars",
        "Chocolates": "bi-heart",
        "Snacks": "bi-cup-straw",
        "Groceries": "bi-basket",
        "Books": "bi-book",
        "Home Appliances": "bi-tv",
        "Sports Products": "bi-dribbble",
        "Accessories": "bi-plug",
        "Other Products": "bi-box-seam"
    }

    category_map = {}
    for cat_name in Config.CATEGORIES:
        icon = cat_icons.get(cat_name, "bi-tag")
        cursor.execute("INSERT INTO categories (category_name, icon) VALUES (?, ?)", (cat_name, icon))
        category_map[cat_name] = cursor.lastrowid

    # 4. Rich Demonstration Products Dataset
    # Covering all 19 categories across Low, Medium, High, and Premium budget ranges
    demo_products = [
        # Bluetooth Earbuds
        {
            "name": "boAt Airdopes 141 ANC TWS Earbuds",
            "brand": "boAt",
            "model": "Airdopes 141 ANC",
            "category": "Bluetooth Earbuds",
            "desc": "Active Noise Cancellation up to 32dB, 42 hours total playtime, ENx tech quad mics, IPX5 water resistance.",
            "image": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&auto=format&fit=crop&q=80",
            "specs": "Bluetooth 5.3, 10mm Drivers, Beast Mode 50ms Low Latency, Type-C ASAP Charge",
            "offers": [
                {"platform": "Amazon", "price": 1299, "orig": 4490, "rating": 4.1, "reviews": 68420, "del": 0, "url": "https://www.amazon.in/dp/B0CB943K18"},
                {"platform": "Flipkart", "price": 1199, "orig": 4490, "rating": 4.2, "reviews": 85210, "del": 40, "url": "https://www.flipkart.com/item/boat-airdopes-141"},
                {"platform": "Meesho", "price": 1149, "orig": 4490, "rating": 4.0, "reviews": 12400, "del": 0, "url": "https://www.meesho.com/boat-airdopes"},
                {"platform": "Croma", "price": 1499, "orig": 4490, "rating": 4.3, "reviews": 4120, "del": 0, "url": "https://www.croma.com/boat-airdopes-141"}
            ]
        },
        {
            "name": "OnePlus Nord Buds 2 True Wireless in Ear Earbuds",
            "brand": "OnePlus",
            "model": "Nord Buds 2",
            "category": "Bluetooth Earbuds",
            "desc": "Up to 25dB Active Noise Cancellation, BassWave enhancement, 12.4mm dynamic titanized drivers, 36 hours battery life.",
            "image": "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=500&auto=format&fit=crop&q=80",
            "specs": "Dolby Atmos Support, IP55 Dust/Water, Fast Charge 10min for 5hrs, Dual Mic AI Call",
            "offers": [
                {"platform": "Amazon", "price": 2499, "orig": 3299, "rating": 4.3, "reviews": 32400, "del": 0, "url": "https://www.amazon.in/dp/B0BY8MCQ9S"},
                {"platform": "Flipkart", "price": 2699, "orig": 3299, "rating": 4.2, "reviews": 29800, "del": 0, "url": "https://www.flipkart.com/oneplus-nord-buds-2"},
                {"platform": "Reliance Digital", "price": 2499, "orig": 3299, "rating": 4.4, "reviews": 5120, "del": 0, "url": "https://www.reliancedigital.in/oneplus-buds-2"},
                {"platform": "Tata CLiQ", "price": 2599, "orig": 3299, "rating": 4.1, "reviews": 1890, "del": 49, "url": "https://www.tatacliq.com/oneplus-nord-buds"}
            ]
        },

        # Mobiles
        {
            "name": "Apple iPhone 15 (128 GB) - Black",
            "brand": "Apple",
            "model": "iPhone 15",
            "category": "Mobiles",
            "desc": "Dynamic Island, 48MP Main Camera with 2x Telephoto, A16 Bionic chip, USB-C connectivity, Ceramic Shield front.",
            "image": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=500&auto=format&fit=crop&q=80",
            "specs": "6.1-inch Super Retina XDR OLED, 128GB ROM, 48MP+12MP Dual Cam, iOS 17, 5G Enabled",
            "offers": [
                {"platform": "Amazon", "price": 65999, "orig": 79900, "rating": 4.6, "reviews": 18230, "del": 0, "url": "https://www.amazon.in/dp/B0CHX1W1XY"},
                {"platform": "Flipkart", "price": 64999, "orig": 79900, "rating": 4.7, "reviews": 24150, "del": 99, "url": "https://www.flipkart.com/apple-iphone-15"},
                {"platform": "Croma", "price": 66900, "orig": 79900, "rating": 4.6, "reviews": 7820, "del": 0, "url": "https://www.croma.com/iphone-15"},
                {"platform": "Reliance Digital", "price": 65490, "orig": 79900, "rating": 4.5, "reviews": 6400, "del": 0, "url": "https://www.reliancedigital.in/iphone-15"}
            ]
        },
        {
            "name": "Samsung Galaxy S24 Ultra 5G (Titanium Gray, 256GB)",
            "brand": "Samsung",
            "model": "Galaxy S24 Ultra",
            "category": "Mobiles",
            "desc": "Galaxy AI features, Titanium frame, 200MP camera system, Built-in S Pen, Snapdragon 8 Gen 3 for Galaxy.",
            "image": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=500&auto=format&fit=crop&q=80",
            "specs": "6.8-inch QHD+ Dynamic AMOLED 2X 120Hz, 12GB RAM, 256GB Storage, 5000mAh Battery",
            "offers": [
                {"platform": "Amazon", "price": 119999, "orig": 134999, "rating": 4.5, "reviews": 4120, "del": 0, "url": "https://www.amazon.in/dp/B0CS5X6Y1X"},
                {"platform": "Flipkart", "price": 121999, "orig": 134999, "rating": 4.6, "reviews": 3890, "del": 0, "url": "https://www.flipkart.com/samsung-s24-ultra"},
                {"platform": "Croma", "price": 119999, "orig": 134999, "rating": 4.7, "reviews": 1200, "del": 0, "url": "https://www.croma.com/samsung-galaxy-s24-ultra"}
            ]
        },

        # Laptops
        {
            "name": "Apple MacBook Air M2 Chip (13.6-inch, 8GB RAM, 256GB SSD)",
            "brand": "Apple",
            "model": "MacBook Air M2",
            "category": "Laptops",
            "desc": "Strikingly thin design, 1080p FaceTime HD camera, MagSafe 3 charging port, up to 18 hours battery life, Liquid Retina display.",
            "image": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500&auto=format&fit=crop&q=80",
            "specs": "Apple M2 8-core CPU / 8-core GPU, 8GB Unified Memory, 256GB SSD, macOS Sonoma, 1.24 kg",
            "offers": [
                {"platform": "Amazon", "price": 84990, "orig": 99900, "rating": 4.7, "reviews": 8940, "del": 0, "url": "https://www.amazon.in/dp/B0B3B97P4F"},
                {"platform": "Flipkart", "price": 86990, "orig": 99900, "rating": 4.7, "reviews": 7200, "del": 0, "url": "https://www.flipkart.com/apple-macbook-air-m2"},
                {"platform": "Reliance Digital", "price": 84490, "orig": 99900, "rating": 4.6, "reviews": 2100, "del": 0, "url": "https://www.reliancedigital.in/macbook-air-m2"}
            ]
        },
        {
            "name": "ASUS Vivobook 15 Intel Core i3 12th Gen Thin and Light",
            "brand": "ASUS",
            "model": "Vivobook 15 X1502ZA",
            "category": "Laptops",
            "desc": "15.6-inch FHD anti-glare display, Intel Core i3-1215U processor, 8GB DDR4 RAM, 512GB NVMe SSD, Windows 11 Home.",
            "image": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=500&auto=format&fit=crop&q=80",
            "specs": "Intel Core i3-1215U (up to 4.4GHz), 8GB RAM, 512GB SSD, 1.7kg, Fast Charge 60% in 49 mins",
            "offers": [
                {"platform": "Amazon", "price": 32990, "orig": 52990, "rating": 4.1, "reviews": 4510, "del": 0, "url": "https://www.amazon.in/dp/ASUS-Vivobook"},
                {"platform": "Flipkart", "price": 31990, "orig": 52990, "rating": 4.2, "reviews": 6120, "del": 40, "url": "https://www.flipkart.com/asus-vivobook-15"},
                {"platform": "Croma", "price": 33990, "orig": 52990, "rating": 4.3, "reviews": 890, "del": 0, "url": "https://www.croma.com/asus-vivobook"}
            ]
        },

        # Headphones
        {
            "name": "Sony WH-1000XM5 Wireless Industry Leading Noise Canceling",
            "brand": "Sony",
            "model": "WH-1000XM5",
            "category": "Headphones",
            "desc": "Two processors and 8 microphones for unprecedented noise cancellation, 30 hours battery, ultra-comfortable soft fit leather.",
            "image": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500&auto=format&fit=crop&q=80",
            "specs": "Auto NC Optimizer, LDAC High-Res Audio, Speak-to-Chat, Multipoint Connection, 3min quick charge = 3hrs",
            "offers": [
                {"platform": "Amazon", "price": 26990, "orig": 34990, "rating": 4.6, "reviews": 7800, "del": 0, "url": "https://www.amazon.in/dp/B09XS7JWHH"},
                {"platform": "Flipkart", "price": 27990, "orig": 34990, "rating": 4.5, "reviews": 5120, "del": 0, "url": "https://www.flipkart.com/sony-wh1000xm5"},
                {"platform": "Croma", "price": 26490, "orig": 34990, "rating": 4.7, "reviews": 1640, "del": 0, "url": "https://www.croma.com/sony-wh-1000xm5"},
                {"platform": "Tata CLiQ", "price": 27499, "orig": 34990, "rating": 4.5, "reviews": 420, "del": 50, "url": "https://www.tatacliq.com/sony-xm5"}
            ]
        },
        {
            "name": "Sony MDR-ZX110A Wired On-Ear Headphones (White)",
            "brand": "Sony",
            "model": "MDR-ZX110A",
            "category": "Headphones",
            "desc": "30mm dynamic dome drivers for balanced sound, high energy neodymium magnets, lightweight folding design for music mobility.",
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&auto=format&fit=crop&q=80",
            "specs": "12Hz–22kHz Frequency Range, 3.5mm Gold-plated Stereo Mini Plug, 1.2m tangle-free cable, 120g weight",
            "offers": [
                {"platform": "Amazon", "price": 899, "orig": 1390, "rating": 4.1, "reviews": 125000, "del": 40, "url": "https://www.amazon.in/dp/B00KGZZ824"},
                {"platform": "Flipkart", "price": 799, "orig": 1390, "rating": 4.2, "reviews": 84200, "del": 40, "url": "https://www.flipkart.com/sony-mdr-zx110a"},
                {"platform": "Meesho", "price": 749, "orig": 1390, "rating": 3.9, "reviews": 6800, "del": 0, "url": "https://www.meesho.com/sony-headphones"},
                {"platform": "Shopsy", "price": 769, "orig": 1390, "rating": 4.0, "reviews": 3200, "del": 0, "url": "https://www.shopsy.in/sony-zx110a"}
            ]
        },

        # Watches
        {
            "name": "Noise ColorFit Pulse 2 Max 1.85'' Smart Watch",
            "brand": "Noise",
            "model": "Pulse 2 Max",
            "category": "Watches",
            "desc": "1.85 inch bright TFT LCD display with 550 nits brightness, Bluetooth calling, 100 sports modes, heart rate and SpO2 monitoring.",
            "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&auto=format&fit=crop&q=80",
            "specs": "10-day battery life, IP68 water resistance, 150+ cloud watch faces, Noise Health Suite",
            "offers": [
                {"platform": "Amazon", "price": 1499, "orig": 5999, "rating": 4.1, "reviews": 43200, "del": 0, "url": "https://www.amazon.in/dp/B0B5383S45"},
                {"platform": "Flipkart", "price": 1399, "orig": 5999, "rating": 4.2, "reviews": 51000, "del": 40, "url": "https://www.flipkart.com/noise-pulse-2-max"},
                {"platform": "Myntra", "price": 1699, "orig": 5999, "rating": 4.3, "reviews": 9800, "del": 0, "url": "https://www.myntra.com/smart-watches/noise"},
                {"platform": "Meesho", "price": 1299, "orig": 5999, "rating": 3.9, "reviews": 11500, "del": 0, "url": "https://www.meesho.com/noise-watch"}
            ]
        },
        {
            "name": "Fossil Grant Chronograph Blue Dial Men's Watch",
            "brand": "Fossil",
            "model": "FS5151",
            "category": "Watches",
            "desc": "Classic Roman numeral hour markers, rich dark blue leather strap, stainless steel round case with quartz chronograph movement.",
            "image": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=500&auto=format&fit=crop&q=80",
            "specs": "44mm Case Diameter, 50m Water Resistance, Genuine Leather 22mm Strap, Mineral Glass",
            "offers": [
                {"platform": "Amazon", "price": 7995, "orig": 12495, "rating": 4.4, "reviews": 3200, "del": 0, "url": "https://www.amazon.in/dp/B0159W7GVK"},
                {"platform": "Flipkart", "price": 8495, "orig": 12495, "rating": 4.3, "reviews": 2100, "del": 0, "url": "https://www.flipkart.com/fossil-grant-watch"},
                {"platform": "Myntra", "price": 7497, "orig": 12495, "rating": 4.5, "reviews": 4600, "del": 0, "url": "https://www.myntra.com/watches/fossil-grant"},
                {"platform": "Tata CLiQ", "price": 7995, "orig": 12495, "rating": 4.4, "reviews": 850, "del": 0, "url": "https://www.tatacliq.com/fossil-grant"}
            ]
        },

        # Shoes
        {
            "name": "Puma Men's Dazzler Sneaker Casual Running Shoes",
            "brand": "Puma",
            "model": "Dazzler",
            "category": "Shoes",
            "desc": "Breathable mesh upper with synthetic overlays, cushioned SoftFoam+ sockliner, flexible EVA midsole for all-day comfort.",
            "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&auto=format&fit=crop&q=80",
            "specs": "Lace-up closure, Rubber traction outsole, Medium width, Lightweight sport profile",
            "offers": [
                {"platform": "Amazon", "price": 1899, "orig": 3999, "rating": 4.1, "reviews": 14200, "del": 0, "url": "https://www.amazon.in/dp/PUMA-Dazzler"},
                {"platform": "Flipkart", "price": 1799, "orig": 3999, "rating": 4.2, "reviews": 22100, "del": 40, "url": "https://www.flipkart.com/puma-dazzler"},
                {"platform": "Myntra", "price": 1999, "orig": 3999, "rating": 4.3, "reviews": 11500, "del": 0, "url": "https://www.myntra.com/shoes/puma-dazzler"},
                {"platform": "AJIO", "price": 1699, "orig": 3999, "rating": 4.1, "reviews": 5600, "del": 99, "url": "https://www.ajio.com/puma-casual-sneakers"}
            ]
        },

        # Men's Clothing
        {
            "name": "Levi's Men's 511 Slim Fit Stretch Denim Jeans",
            "brand": "Levi's",
            "model": "511 Slim",
            "category": "Men’s Clothing",
            "desc": "A modern slim with room to move, added stretch for all-day mobility, authentic 5-pocket styling and classic red tab.",
            "image": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=500&auto=format&fit=crop&q=80",
            "specs": "99% Cotton, 1% Elastane, Mid-rise, Zip fly with button closure, Machine wash cold",
            "offers": [
                {"platform": "Amazon", "price": 2199, "orig": 3999, "rating": 4.2, "reviews": 7500, "del": 0, "url": "https://www.amazon.in/dp/LEVIS-511"},
                {"platform": "Myntra", "price": 1999, "orig": 3999, "rating": 4.4, "reviews": 15800, "del": 0, "url": "https://www.myntra.com/jeans/levis-511"},
                {"platform": "AJIO", "price": 2099, "orig": 3999, "rating": 4.3, "reviews": 8400, "del": 0, "url": "https://www.ajio.com/levis-slim-jeans"},
                {"platform": "Tata CLiQ", "price": 2299, "orig": 3999, "rating": 4.1, "reviews": 1200, "del": 0, "url": "https://www.tatacliq.com/levis-511"}
            ]
        },

        # Women's Clothing
        {
            "name": "Biba Women Floral Printed Pure Cotton Anarkali Kurta Set",
            "brand": "Biba",
            "model": "Anarkali Set",
            "category": "Women’s Clothing",
            "desc": "Vibrant floral print pure cotton Anarkali kurta with matching solid trousers and lightweight printed mulmul dupatta.",
            "image": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=500&auto=format&fit=crop&q=80",
            "specs": "100% Breathable Cotton, Calf-length flared hem, Round neck with keyhole, Hand wash recommended",
            "offers": [
                {"platform": "Myntra", "price": 2499, "orig": 5995, "rating": 4.4, "reviews": 6800, "del": 0, "url": "https://www.myntra.com/kurta-sets/biba"},
                {"platform": "AJIO", "price": 2399, "orig": 5995, "rating": 4.3, "reviews": 4200, "del": 0, "url": "https://www.ajio.com/biba-anarkali-suit"},
                {"platform": "Flipkart", "price": 2699, "orig": 5995, "rating": 4.1, "reviews": 3100, "del": 40, "url": "https://www.flipkart.com/biba-kurta-set"},
                {"platform": "Amazon", "price": 2599, "orig": 5995, "rating": 4.2, "reviews": 2900, "del": 0, "url": "https://www.amazon.in/dp/BIBA-Kurta-Set"}
            ]
        },

        # Bags
        {
            "name": "American Tourister Valex 28L Water Resistant Laptop Backpack",
            "brand": "American Tourister",
            "model": "Valex 28L",
            "category": "Bags",
            "desc": "Spacious 3 compartments with dedicated 15.6 inch padded laptop cradle, Tractum suspension straps, side bottle pocket.",
            "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&auto=format&fit=crop&q=80",
            "specs": "Water-resistant Polyester fabric, Rain cover included, Ergonomic mesh back padding, 1-Year Warranty",
            "offers": [
                {"platform": "Amazon", "price": 1299, "orig": 2900, "rating": 4.3, "reviews": 18400, "del": 0, "url": "https://www.amazon.in/dp/B0B64D9T5Y"},
                {"platform": "Flipkart", "price": 1199, "orig": 2900, "rating": 4.3, "reviews": 24500, "del": 40, "url": "https://www.flipkart.com/american-tourister-valex"},
                {"platform": "Myntra", "price": 1399, "orig": 2900, "rating": 4.4, "reviews": 7100, "del": 0, "url": "https://www.myntra.com/backpacks/american-tourister"},
                {"platform": "Meesho", "price": 1099, "orig": 2900, "rating": 3.9, "reviews": 4200, "del": 0, "url": "https://www.meesho.com/at-valex-bag"}
            ]
        },

        # Beauty Products
        {
            "name": "Maybelline New York Fit Me Matte+Poreless Liquid Foundation",
            "brand": "Maybelline",
            "model": "Fit Me 128",
            "category": "Beauty Products",
            "desc": "Natural matte finish, refines pores and leaves a flawless natural look, oil-free formula with SPF 22.",
            "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=500&auto=format&fit=crop&q=80",
            "specs": "30ml Pump Bottle, Dermatologist tested, Allergy tested, Non-comedogenic",
            "offers": [
                {"platform": "Nykaa", "price": 499, "orig": 699, "rating": 4.5, "reviews": 89400, "del": 0, "url": "https://www.nykaa.com/maybelline-fit-me-foundation"},
                {"platform": "Amazon", "price": 475, "orig": 699, "rating": 4.3, "reviews": 54200, "del": 40, "url": "https://www.amazon.in/dp/B073X7P64Z"},
                {"platform": "Flipkart", "price": 489, "orig": 699, "rating": 4.4, "reviews": 61200, "del": 40, "url": "https://www.flipkart.com/maybelline-fit-me"},
                {"platform": "Myntra", "price": 524, "orig": 699, "rating": 4.5, "reviews": 32100, "del": 0, "url": "https://www.myntra.com/makeup/maybelline-fit-me"}
            ]
        },
        {
            "name": "NIVEA Soft Light Moisturizing Cream, Vitamin E & Jojoba Oil 300ml",
            "brand": "Nivea",
            "model": "Soft 300ml",
            "category": "Beauty Products",
            "desc": "Non-greasy, fast-absorbing refreshing cream for face, body, and hands with Jojoba oil and Vitamin E.",
            "image": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=500&auto=format&fit=crop&q=80",
            "specs": "300ml Jar, Suitable for all skin types, Fresh floral fragrance",
            "offers": [
                {"platform": "Amazon", "price": 280, "orig": 420, "rating": 4.4, "reviews": 62100, "del": 40, "url": "https://www.amazon.in/dp/NIVEA-Soft-300"},
                {"platform": "Nykaa", "price": 299, "orig": 420, "rating": 4.5, "reviews": 38400, "del": 0, "url": "https://www.nykaa.com/nivea-soft-cream"},
                {"platform": "Flipkart", "price": 270, "orig": 420, "rating": 4.4, "reviews": 41200, "del": 40, "url": "https://www.flipkart.com/nivea-soft"},
                {"platform": "Meesho", "price": 255, "orig": 420, "rating": 4.1, "reviews": 9800, "del": 0, "url": "https://www.meesho.com/nivea-soft"}
            ]
        },

        # Chocolates
        {
            "name": "Cadbury Dairy Milk Silk Hazelnut Chocolate Bar (143g)",
            "brand": "Cadbury",
            "model": "Silk Hazelnut",
            "category": "Chocolates",
            "desc": "Luscious creamy smooth chocolate wrapped around crunchy whole hazelnuts for an indulgent bite.",
            "image": "https://images.unsplash.com/photo-1549007994-cb92caebd54b?w=500&auto=format&fit=crop&q=80",
            "specs": "143 grams bar, 100% vegetarian, Sealed freshness pack, Rich cocoa butter",
            "offers": [
                {"platform": "Amazon", "price": 175, "orig": 210, "rating": 4.5, "reviews": 32000, "del": 30, "url": "https://www.amazon.in/dp/Cadbury-Silk-Hazelnut"},
                {"platform": "Flipkart", "price": 170, "orig": 210, "rating": 4.5, "reviews": 21000, "del": 40, "url": "https://www.flipkart.com/cadbury-silk-hazelnut"},
                {"platform": "Shopsy", "price": 165, "orig": 210, "rating": 4.3, "reviews": 4300, "del": 0, "url": "https://www.shopsy.in/cadbury-silk"}
            ]
        },

        # Snacks
        {
            "name": "Haldiram's Nagpur Aloo Bhujia Crispy Snack (1 kg Pack)",
            "brand": "Haldiram's",
            "model": "Aloo Bhujia 1kg",
            "category": "Snacks",
            "desc": "Iconic Indian crispy spiced potato & gram flour noodles, flavored with tangy mint and chili masala.",
            "image": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=500&auto=format&fit=crop&q=80",
            "specs": "1 Kilogram pouch, Zero trans fat, Authentic spicy recipe",
            "offers": [
                {"platform": "Amazon", "price": 235, "orig": 270, "rating": 4.4, "reviews": 18200, "del": 40, "url": "https://www.amazon.in/dp/Haldirams-Aloo-Bhujia"},
                {"platform": "Flipkart", "price": 240, "orig": 270, "rating": 4.3, "reviews": 14500, "del": 40, "url": "https://www.flipkart.com/haldirams-bhujia"},
                {"platform": "Shopsy", "price": 220, "orig": 270, "rating": 4.2, "reviews": 3800, "del": 0, "url": "https://www.shopsy.in/haldirams-aloo-bhujia"}
            ]
        },

        # Groceries
        {
            "name": "Fortune Sunlite Refined Sunflower Cooking Oil (1 Litre Pouch)",
            "brand": "Fortune",
            "model": "Sunlite 1L",
            "category": "Groceries",
            "desc": "Light, healthy and easy to digest cooking oil enriched with vitamins A, D, and E for active lifestyle.",
            "image": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&auto=format&fit=crop&q=80",
            "specs": "1000ml Pouch, Low absorb technology, Fortified with micronutrients",
            "offers": [
                {"platform": "Amazon", "price": 142, "orig": 175, "rating": 4.4, "reviews": 38100, "del": 40, "url": "https://www.amazon.in/dp/Fortune-Sunlite-1L"},
                {"platform": "Flipkart", "price": 139, "orig": 175, "rating": 4.3, "reviews": 29800, "del": 40, "url": "https://www.flipkart.com/fortune-sunlite"},
                {"platform": "Shopsy", "price": 135, "orig": 175, "rating": 4.1, "reviews": 6400, "del": 0, "url": "https://www.shopsy.in/fortune-oil"}
            ]
        },

        # Books
        {
            "name": "Atomic Habits: An Easy & Proven Way to Build Good Habits by James Clear",
            "brand": "Random House",
            "model": "Paperback Edition",
            "category": "Books",
            "desc": "World-renowned bestseller teaching how tiny changes can lead to remarkable results in work and daily personal life.",
            "image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80",
            "specs": "English, 320 pages, Paperback, Self-Help / Productivity genre",
            "offers": [
                {"platform": "Amazon", "price": 420, "orig": 799, "rating": 4.7, "reviews": 94000, "del": 40, "url": "https://www.amazon.in/dp/1847941834"},
                {"platform": "Flipkart", "price": 399, "orig": 799, "rating": 4.6, "reviews": 72500, "del": 40, "url": "https://www.flipkart.com/atomic-habits"},
                {"platform": "Meesho", "price": 289, "orig": 799, "rating": 4.1, "reviews": 11200, "del": 0, "url": "https://www.meesho.com/atomic-habits-book"}
            ]
        },

        # Home Appliances
        {
            "name": "Prestige Iris 750 Watt Mixer Grinder with 3 Stainless Steel Jars",
            "brand": "Prestige",
            "model": "Iris 750W",
            "category": "Home Appliances",
            "desc": "Heavy-duty 750 watt copper motor, 3 stainless steel jars (wet, dry, chutney) and 1 transparent juicer jar with safety lock.",
            "image": "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?w=500&auto=format&fit=crop&q=80",
            "specs": "750 Watts, 3 Speed Control with Incher, Overload protection switch, 2-Year warranty",
            "offers": [
                {"platform": "Amazon", "price": 3199, "orig": 6295, "rating": 4.0, "reviews": 46200, "del": 0, "url": "https://www.amazon.in/dp/Prestige-Iris-750"},
                {"platform": "Flipkart", "price": 2999, "orig": 6295, "rating": 4.1, "reviews": 58900, "del": 99, "url": "https://www.flipkart.com/prestige-iris-mixer"},
                {"platform": "Croma", "price": 3299, "orig": 6295, "rating": 4.2, "reviews": 4300, "del": 0, "url": "https://www.croma.com/prestige-iris"},
                {"platform": "Reliance Digital", "price": 3150, "orig": 6295, "rating": 4.1, "reviews": 3100, "del": 0, "url": "https://www.reliancedigital.in/prestige-mixer"}
            ]
        },

        # Sports Products
        {
            "name": "Yonex Nanoray 70 Light Carbon Graphite Badminton Racquet",
            "brand": "Yonex",
            "model": "Nanoray 70 Light",
            "category": "Sports Products",
            "desc": "Ultra lightweight head-light balance for lightning-fast shot recovery, Isometric frame shape for 7% enlarged sweet spot.",
            "image": "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=500&auto=format&fit=crop&q=80",
            "specs": "77 grams (5U), String tension up to 30 lbs, Full graphite shaft, Full racquet cover included",
            "offers": [
                {"platform": "Amazon", "price": 1899, "orig": 3490, "rating": 4.2, "reviews": 11500, "del": 0, "url": "https://www.amazon.in/dp/Yonex-Nanoray-70"},
                {"platform": "Flipkart", "price": 1749, "orig": 3490, "rating": 4.3, "reviews": 15800, "del": 40, "url": "https://www.flipkart.com/yonex-nanoray-70"},
                {"platform": "Tata CLiQ", "price": 1999, "orig": 3490, "rating": 4.1, "reviews": 920, "del": 0, "url": "https://www.tatacliq.com/yonex-racquet"}
            ]
        },

        # Accessories
        {
            "name": "boAt Rugged v3 Extra Tough Braided Type-C Fast Charging Cable (1.5 Meter)",
            "brand": "boAt",
            "model": "Rugged v3 Type-C",
            "category": "Accessories",
            "desc": "Indestructible braided nylon exterior tested for 10,000+ bends, 3A fast charging and 480 Mbps high-speed data sync.",
            "image": "https://images.unsplash.com/photo-1541689592655-f5f52825a3b8?w=500&auto=format&fit=crop&q=80",
            "specs": "1.5m Length, Aluminum alloy connectors, QC 3.0 Compatible, 2-Year warranty",
            "offers": [
                {"platform": "Amazon", "price": 249, "orig": 799, "rating": 4.2, "reviews": 38900, "del": 40, "url": "https://www.amazon.in/dp/boAt-TypeC-Cable"},
                {"platform": "Flipkart", "price": 229, "orig": 799, "rating": 4.3, "reviews": 44100, "del": 40, "url": "https://www.flipkart.com/boat-typec-cable"},
                {"platform": "Meesho", "price": 189, "orig": 799, "rating": 4.0, "reviews": 8400, "del": 0, "url": "https://www.meesho.com/boat-cable"},
                {"platform": "Shopsy", "price": 199, "orig": 799, "rating": 4.1, "reviews": 3200, "del": 0, "url": "https://www.shopsy.in/boat-cable"}
            ]
        },

        # Electronics
        {
            "name": "SanDisk Ultra 128GB MicroSDXC UHS-I Memory Card 140MB/s",
            "brand": "SanDisk",
            "model": "Ultra 128GB",
            "category": "Electronics",
            "desc": "Fast read speeds up to 140MB/s to transfer 1000 photos in a minute, A1 rated for faster app performance and Full HD recording.",
            "image": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500&auto=format&fit=crop&q=80",
            "specs": "128GB, Class 10, UHS-I, Waterproof, Temperature-proof, X-ray proof, 10-Year warranty",
            "offers": [
                {"platform": "Amazon", "price": 899, "orig": 1800, "rating": 4.4, "reviews": 112000, "del": 40, "url": "https://www.amazon.in/dp/SanDisk-128GB"},
                {"platform": "Flipkart", "price": 849, "orig": 1800, "rating": 4.4, "reviews": 98000, "del": 40, "url": "https://www.flipkart.com/sandisk-128gb"},
                {"platform": "Croma", "price": 949, "orig": 1800, "rating": 4.5, "reviews": 6400, "del": 0, "url": "https://www.croma.com/sandisk-128gb"}
            ]
        },

        # Other Products
        {
            "name": "Wipro 16A Smart Wi-Fi Plug with Energy Monitoring and Voice Control",
            "brand": "Wipro",
            "model": "Smart Plug 16A",
            "category": "Other Products",
            "desc": "Control heavy appliances like AC, geyser, microwave from anywhere using Wipro Next Smart Home App. Works with Alexa and Google Assistant.",
            "image": "https://images.unsplash.com/photo-1558002038-1055907df827?w=500&auto=format&fit=crop&q=80",
            "specs": "16 Ampere rating, Wi-Fi 2.4GHz, Real-time energy consumption tracker, Scheduling timer",
            "offers": [
                {"platform": "Amazon", "price": 999, "orig": 2290, "rating": 4.1, "reviews": 15400, "del": 0, "url": "https://www.amazon.in/dp/Wipro-16A-SmartPlug"},
                {"platform": "Flipkart", "price": 949, "orig": 2290, "rating": 4.2, "reviews": 18200, "del": 40, "url": "https://www.flipkart.com/wipro-smart-plug"},
                {"platform": "Reliance Digital", "price": 999, "orig": 2290, "rating": 4.3, "reviews": 2100, "del": 0, "url": "https://www.reliancedigital.in/wipro-plug"}
            ]
        }
    ]

    # Insert Products and Offers
    for p_info in demo_products:
        cat_id = category_map.get(p_info["category"])
        if not cat_id:
            # Fallback
            cat_id = category_map["Other Products"]

        cursor.execute("""
        INSERT INTO products (product_name, brand, model, category_id, description, image_url, specifications)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (p_info["name"], p_info["brand"], p_info["model"], cat_id, p_info["desc"], p_info["image"], p_info["specs"]))
        
        prod_id = cursor.lastrowid

        # Insert Offers for this Product
        for offer_item in p_info["offers"]:
            plat_id = platform_map.get(offer_item["platform"])
            if not plat_id:
                plat_id = list(platform_map.values())[0]

            cursor.execute("""
            INSERT INTO product_offers (product_id, platform_id, current_price, original_price,
                                        rating, review_count, product_url, delivery_charge,
                                        availability, data_source, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'In Stock', 'DEMONSTRATION', ?)
            """, (
                prod_id,
                plat_id,
                float(offer_item["price"]),
                float(offer_item["orig"]),
                float(offer_item["rating"]),
                int(offer_item["reviews"]),
                offer_item["url"],
                float(offer_item["del"]),
                now_str
            ))
            offer_id = cursor.lastrowid

            # Generate 4 realistic historical price points for Price History charts
            # Days: 30 days ago, 20 days ago, 10 days ago, today
            base_price = offer_item["price"]
            for days_ago, multiplier in [(30, 1.15), (20, 1.08), (10, 0.98), (1, 1.0)]:
                rec_date = (datetime.utcnow() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
                rec_price = round(base_price * multiplier, 2)
                cursor.execute("""
                INSERT INTO price_history (offer_id, recorded_price, recorded_at)
                VALUES (?, ?, ?)
                """, (offer_id, rec_price, rec_date))

    # Add initial search history item for demo
    cursor.execute("""
    INSERT INTO search_history (user_id, search_query, searched_at)
    VALUES (2, 'Bluetooth Earbuds', ?)
    """, (now_str,))
    cursor.execute("""
    INSERT INTO search_history (user_id, search_query, searched_at)
    VALUES (2, 'iPhone 15', ?)
    """, (now_str,))

    conn.commit()
    conn.close()
    print("Demonstration data seeded successfully across all categories and platforms!")


if __name__ == "__main__":
    init_db()
    seed_data()
