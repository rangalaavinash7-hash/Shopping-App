"""
ShopFinder Product Service (Python Syllabus Units I, II, III & IV)
Contains business logic, reusable functions, database queries, and Trie suggestions.
"""

from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime
import json
import sqlite3

from database import get_db_connection
from models import Product, ProductOffer
from algorithms.search import linear_search_products, SearchTrie
from algorithms.sorting import merge_sort_products
from config import Config


# Global Trie instance initialized on startup for blazing-fast auto-suggestions
_global_trie = SearchTrie()
_trie_initialized = False


def init_search_trie():
    """Populates the in-memory Trie with all product names, brands, and categories."""
    global _global_trie, _trie_initialized
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.product_name, p.brand, c.category_name, p.image_url
        FROM products p
        JOIN categories c ON p.category_id = c.id
    """)
    rows = cursor.fetchall()
    conn.close()

    _global_trie = SearchTrie()
    for row in rows:
        prod_id, name, brand, cat_name, img = row["id"], row["product_name"], row["brand"], row["category_name"], row["image_url"]
        payload = {"id": prod_id, "title": name, "brand": brand, "category": cat_name, "image": img}
        _global_trie.insert(name, payload)
        # Also index by brand
        _global_trie.insert(brand, {"title": f"{brand} ({cat_name})", "brand": brand, "category": cat_name})
    
    _trie_initialized = True
    print("Search Trie initialized with product vocabulary.")


def get_search_suggestions(prefix: str, limit: int = 6) -> List[Dict[str, Any]]:
    """Retrieves autocomplete suggestions from the Trie data structure (O(L))."""
    global _trie_initialized
    if not _trie_initialized:
        init_search_trie()
    return _global_trie.autocomplete(prefix, limit=limit)


# -------------------------------------------------------------
# Unit II: Functions and Types of Functions
# -------------------------------------------------------------

def calculate_discount(original_price: float, current_price: float) -> int:
    """
    Unit I & II: Calculates the percentage savings.
    Uses conditional operators to guard against zero-division and invalid prices.
    """
    if original_price > current_price and original_price > 0:
        savings = original_price - current_price
        return int(round((savings / original_price) * 100))
    return 0


def filter_by_budget(products: List[Dict[str, Any]], min_price: float = 0.0, 
                     max_price: Optional[float] = None) -> List[Dict[str, Any]]:
    """
    Filters product list according to user budget constraints.
    Demonstrates loops and conditional statements (Unit I).
    """
    filtered = []
    for p in products:
        price = p.get("min_price", 0.0)
        # Check lower bound
        if price < min_price:
            continue
        # Check upper bound
        if max_price is not None and price > max_price:
            continue
        filtered.append(p)
    return filtered


def sort_products_by_price(products: List[Dict[str, Any]], reverse: bool = False) -> List[Dict[str, Any]]:
    """
    Sorts product list using Merge Sort (ADS Module).
    """
    return merge_sort_products(products, key="min_price", reverse=reverse)


def validate_product_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validates product creation and editing fields.
    Returns (is_valid: bool, error_message: str). Demonstrates tuples (Unit III).
    """
    if not data.get("product_name") or len(data["product_name"].strip()) < 3:
        return False, "Product name must be at least 3 characters long."
    if not data.get("brand") or len(data["brand"].strip()) < 2:
        return False, "Brand name is required."
    if not data.get("category_id"):
        return False, "Category selection is required."
    return True, ""


# -------------------------------------------------------------
# Database Retrieval & Filtering
# -------------------------------------------------------------

def get_all_categories() -> List[Dict[str, Any]]:
    """Fetches all 19 product categories with product counts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.category_name, c.icon, COUNT(p.id) AS product_count
        FROM categories c
        LEFT JOIN products p ON c.id = p.category_id
        GROUP BY c.id
        ORDER BY c.category_name ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_brands() -> List[str]:
    """
    Demonstrates Unit III: Sets
    Extracts unique brand names from products using a set for deduplication.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT brand FROM products")
    rows = cursor.fetchall()
    conn.close()

    # Using Python set to eliminate duplicates
    unique_brands: Set[str] = {r["brand"] for r in rows if r["brand"]}
    return sorted(list(unique_brands))


def get_products(query: str = "", category_id: Optional[int] = None,
                 platform_id: Optional[int] = None, min_price: float = 0.0,
                 max_price: Optional[float] = None, min_rating: float = 0.0,
                 sort_by: str = "relevance", sort_order: str = "asc",
                 limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """
    Comprehensive search and filter function.
    Calls database queries and passes items through Linear Search and Merge Sort.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Base query joining products, categories, and offers
    sql = """
        SELECT 
            p.id, p.product_name, p.brand, p.model, p.category_id,
            p.description, p.image_url, p.specifications,
            c.category_name,
            MIN(po.current_price) as min_price,
            MAX(po.current_price) as max_price,
            MAX(po.rating) as best_rating,
            COUNT(po.id) as offers_count
        FROM products p
        JOIN categories c ON p.category_id = c.id
        LEFT JOIN product_offers po ON p.id = po.product_id
        WHERE 1=1
    """
    params = []

    if category_id:
        sql += " AND p.category_id = ?"
        params.append(category_id)

    if platform_id:
        sql += " AND po.platform_id = ?"
        params.append(platform_id)

    sql += " GROUP BY p.id"

    cursor.execute(sql, params)
    raw_products = [dict(r) for r in cursor.fetchall()]

    # Fetch offers for each product to calculate best discounts and total costs
    for prod in raw_products:
        cursor.execute("""
            SELECT po.*, pl.platform_name, pl.logo_icon
            FROM product_offers po
            JOIN platforms pl ON po.platform_id = pl.id
            WHERE po.product_id = ?
            ORDER BY (po.current_price + po.delivery_charge) ASC
        """, (prod["id"],))
        offers = [dict(o) for o in cursor.fetchall()]
        
        # Calculate calculated fields
        for o in offers:
            o["total_cost"] = round(o["current_price"] + o["delivery_charge"], 2)
            o["discount_percentage"] = calculate_discount(o["original_price"], o["current_price"])

        prod["offers"] = offers
        if offers:
            best_offer = offers[0]
            prod["min_price"] = best_offer["current_price"]
            prod["min_total_cost"] = best_offer["total_cost"]
            prod["best_platform"] = best_offer["platform_name"]
            prod["best_platform_logo"] = best_offer["logo_icon"]
            prod["best_discount"] = max(o["discount_percentage"] for o in offers)
            prod["best_rating"] = max(o["rating"] for o in offers)
            highest_offer = max(offers, key=lambda x: x["total_cost"])
            prod["max_savings"] = round(highest_offer["total_cost"] - best_offer["total_cost"], 2)
        else:
            prod["min_price"] = 0.0
            prod["min_total_cost"] = 0.0
            prod["best_platform"] = ""
            prod["best_platform_logo"] = ""
            prod["best_discount"] = 0
            prod["best_rating"] = 0.0
            prod["max_savings"] = 0.0

    conn.close()

    # 1. Apply Search Filter using Linear Search Algorithm (algorithms/search.py)
    if query and query.strip():
        raw_products = linear_search_products(raw_products, query)

    # 2. Apply Budget Range Filter
    filtered_products = filter_by_budget(raw_products, min_price=min_price, max_price=max_price)

    # 3. Apply Minimum Rating Filter
    if min_rating > 0:
        filtered_products = [p for p in filtered_products if p.get("best_rating", 0) >= min_rating]

    # 4. Apply Sorting using Merge Sort (algorithms/sorting.py)
    if sort_by == "price":
        reverse = (sort_order.lower() == "desc")
        filtered_products = merge_sort_products(filtered_products, key="min_price", reverse=reverse)
    elif sort_by == "rating":
        filtered_products = merge_sort_products(filtered_products, key="best_rating", reverse=True)
    elif sort_by == "discount":
        filtered_products = merge_sort_products(filtered_products, key="best_discount", reverse=True)
    elif sort_by == "savings":
        filtered_products = merge_sort_products(filtered_products, key="max_savings", reverse=True)

    total_count = len(filtered_products)
    paginated = filtered_products[offset:offset + limit]

    return {
        "products": paginated,
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total_count
    }


def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    """Fetches single product details with all associated platform offers."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.*, c.category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE p.id = ?
    """, (product_id,))
    prod_row = cursor.fetchone()
    if not prod_row:
        conn.close()
        return None

    product = dict(prod_row)

    cursor.execute("""
        SELECT po.*, pl.platform_name, pl.website_url, pl.logo_icon
        FROM product_offers po
        JOIN platforms pl ON po.platform_id = pl.id
        WHERE po.product_id = ?
        ORDER BY (po.current_price + po.delivery_charge) ASC
    """, (product_id,))
    offers = [dict(o) for o in cursor.fetchall()]

    for o in offers:
        o["total_cost"] = round(o["current_price"] + o["delivery_charge"], 2)
        o["discount_percentage"] = calculate_discount(o["original_price"], o["current_price"])

    product["offers"] = offers
    if offers:
        product["min_price"] = offers[0]["current_price"]
        product["min_total_cost"] = offers[0]["total_cost"]
        product["best_platform"] = offers[0]["platform_name"]
        product["best_discount"] = max(o["discount_percentage"] for o in offers)
        product["best_rating"] = max(o["rating"] for o in offers)
        highest = max(offers, key=lambda x: x["total_cost"])
        product["max_savings"] = round(highest["total_cost"] - offers[0]["total_cost"], 2)

    conn.close()
    return product


# -------------------------------------------------------------
# Admin CRUD Operations
# -------------------------------------------------------------

def create_product(data: Dict[str, Any]) -> int:
    """Inserts a new product into the database and refreshes the search Trie."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (product_name, brand, model, category_id, description, image_url, specifications)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["product_name"],
        data["brand"],
        data.get("model", ""),
        data["category_id"],
        data.get("description", ""),
        data.get("image_url", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"),
        data.get("specifications", "")
    ))
    new_id = cursor.lastrowid

    # If offers provided, insert them
    offers = data.get("offers", [])
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    for off in offers:
        cursor.execute("""
            INSERT INTO product_offers (product_id, platform_id, current_price, original_price,
                                        rating, review_count, product_url, delivery_charge,
                                        availability, data_source, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'In Stock', 'ADMIN_ENTRY', ?)
        """, (
            new_id,
            off["platform_id"],
            float(off["current_price"]),
            float(off.get("original_price", off["current_price"])),
            float(off.get("rating", 4.0)),
            int(off.get("review_count", 100)),
            off.get("product_url", "#"),
            float(off.get("delivery_charge", 0.0)),
            now_str
        ))

    conn.commit()
    conn.close()

    # Refresh Trie
    init_search_trie()
    return new_id


def update_product(product_id: int, data: Dict[str, Any]) -> bool:
    """Updates an existing product."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET product_name = ?, brand = ?, model = ?, category_id = ?,
            description = ?, image_url = ?, specifications = ?
        WHERE id = ?
    """, (
        data["product_name"],
        data["brand"],
        data.get("model", ""),
        data["category_id"],
        data.get("description", ""),
        data.get("image_url", ""),
        data.get("specifications", ""),
        product_id
    ))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()

    init_search_trie()
    return rows_affected > 0


def delete_product(product_id: int) -> bool:
    """Deletes a product and cascades to its offers."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()

    init_search_trie()
    return rows_affected > 0
