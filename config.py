import os

class Config:
    """
    ShopFinder Application Configuration
    Includes paths, secret keys, budget boundaries, and platform settings.
    """
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, "database", "shopfinder.db")
    LOG_FILE_PATH = os.path.join(BASE_DIR, "app.log")
    SECRET_KEY = os.environ.get("SECRET_KEY", "shopfinder-super-secret-key-2026-secure")
    
    # Session Configuration
    SESSION_COOKIE_NAME = "shopfinder_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    
    # Configurable Budget Boundaries (₹ INR)
    BUDGET_TIERS = {
        "low": {"name": "Low Budget", "min": 0, "max": 500, "label": "₹0 - ₹500"},
        "medium": {"name": "Medium Budget", "min": 501, "max": 3000, "label": "₹501 - ₹3,000"},
        "high": {"name": "High Budget", "min": 3001, "max": 10000, "label": "₹3,001 - ₹10,000"},
        "premium": {"name": "Premium", "min": 10001, "max": 1000000, "label": "Above ₹10,000"}
    }
    
    # 19 Required Product Categories
    CATEGORIES = [
        "Mobiles",
        "Laptops",
        "Electronics",
        "Bluetooth Earbuds",
        "Headphones",
        "Men’s Clothing",
        "Women’s Clothing",
        "Shoes",
        "Watches",
        "Bags",
        "Beauty Products",
        "Chocolates",
        "Snacks",
        "Groceries",
        "Books",
        "Home Appliances",
        "Sports Products",
        "Accessories",
        "Other Products"
    ]
    
    # Supported E-Commerce Platforms
    PLATFORMS = [
        {"name": "Amazon", "url": "https://www.amazon.in", "logo": "amazon", "tag": "Global Leader"},
        {"name": "Flipkart", "url": "https://www.flipkart.com", "logo": "flipkart", "tag": "Big Billion Deals"},
        {"name": "Meesho", "url": "https://www.meesho.com", "logo": "meesho", "tag": "Lowest Wholesale"},
        {"name": "Shopsy", "url": "https://www.shopsy.in", "logo": "shopsy", "tag": "Budget Friendly"},
        {"name": "Myntra", "url": "https://www.myntra.com", "logo": "myntra", "tag": "Fashion & Trends"},
        {"name": "AJIO", "url": "https://www.ajio.com", "logo": "ajio", "tag": "Doubt is Out"},
        {"name": "Tata CLiQ", "url": "https://www.tatacliq.com", "logo": "tatacliq", "tag": "Tata Authenticity"},
        {"name": "Croma", "url": "https://www.croma.com", "logo": "croma", "tag": "Gadget Expert"},
        {"name": "Reliance Digital", "url": "https://www.reliancedigital.in", "logo": "reliance", "tag": "Tech Destined"},
        {"name": "Nykaa", "url": "https://www.nykaa.com", "logo": "nykaa", "tag": "Beauty & Wellness"}
    ]
