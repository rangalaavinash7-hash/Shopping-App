"""
ShopFinder: Full-Stack Shopping Comparison Engine
Python Flask Backend & RESTful API Architecture
Integrates Python Syllabus Units I, II, III, IV, and V, SQLite Database, and ADS Algorithms.
"""

import os
import logging
from datetime import datetime
from functools import wraps
import json
import xml.etree.ElementTree as ET

from flask import (
    Flask, request, jsonify, render_template, session,
    redirect, url_for, flash, send_file, Response
)
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

from config import Config
from database import get_db_connection, init_db, seed_data
from services.product_service import (
    get_products, get_product_by_id, get_all_categories,
    get_all_brands, get_search_suggestions, create_product,
    update_product, delete_product, init_search_trie,
    validate_product_data
)
from services.comparison_service import (
    compare_products_side_by_side,
    compare_product_platform_offers,
    get_offer_price_history
)
from services.platform_service import get_all_platforms
from algorithms.recommendations import rank_recommended_products

# Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)

# -------------------------------------------------------------
# Unit IV: File Handling & Application Logging
# -------------------------------------------------------------
logging.basicConfig(
    filename=Config.LOG_FILE_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ShopFinder")
logger.info("ShopFinder system initializing...")


# Authentication Helper Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required. Please login."}), 401
            return redirect(url_for("login_page", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Admin privileges required."}), 403
            flash("Admin privileges required.", "error")
            return redirect(url_for("home_page"))
        return f(*args, **kwargs)
    return decorated_function


# -------------------------------------------------------------
# HTML Template Rendering Routes
# -------------------------------------------------------------

@app.route("/")
def home_page():
    """Renders the purple-and-white hero home page with platform cards & featured deals."""
    categories = get_all_categories()
    platforms = get_all_platforms()
    # Featured products: top recommended items across categories
    featured_data = get_products(limit=8, sort_by="savings")
    return render_template(
        "index.html",
        categories=categories,
        platforms=platforms,
        featured_products=featured_data["products"],
        budget_tiers=Config.BUDGET_TIERS
    )


@app.route("/products")
def products_page():
    """Renders full catalog with dynamic sidebar filters, budget tiers, and search."""
    categories = get_all_categories()
    platforms = get_all_platforms()
    brands = get_all_brands()
    return render_template(
        "products.html",
        categories=categories,
        platforms=platforms,
        brands=brands,
        budget_tiers=Config.BUDGET_TIERS
    )


@app.route("/compare")
def compare_page():
    """Renders the side-by-side product comparison and platform price chart page."""
    categories = get_all_categories()
    return render_template("compare.html", categories=categories)


@app.route("/wishlist")
@login_required
def wishlist_page():
    """Renders the user's saved wishlist."""
    return render_template("wishlist.html")


@app.route("/history")
def history_page():
    """Renders search queries history and recently viewed products."""
    return render_template("history.html")


@app.route("/login")
def login_page():
    """Renders the user authentication login page."""
    if "user_id" in session:
        return redirect(url_for("home_page"))
    return render_template("login.html")


@app.route("/register")
def register_page():
    """Renders user registration page."""
    if "user_id" in session:
        return redirect(url_for("home_page"))
    return render_template("register.html")


@app.route("/admin")
@admin_required
def admin_page():
    """Renders admin management panel with product CRUD & Pandas analytics."""
    categories = get_all_categories()
    platforms = get_all_platforms()
    return render_template("admin.html", categories=categories, platforms=platforms)


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/contact")
def contact_page():
    return render_template("contact.html")


# -------------------------------------------------------------
# REST API Endpoints (Unit V: JSON Processing)
# -------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def api_health():
    """System health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "application": "ShopFinder Smart Shopping Engine",
        "version": "1.0.0",
        "database": "SQLite3 (shopfinder.db)"
    }), 200


@app.route("/api/products", methods=["GET"])
def api_get_products():
    """
    Retrieves filtered, sorted, and paginated products.
    Accepts query parameters: q, category_id, platform_id, min_price, max_price, min_rating, sort_by, sort_order.
    """
    query = request.args.get("q", "")
    category_id = request.args.get("category_id", type=int)
    platform_id = request.args.get("platform_id", type=int)
    min_price = request.args.get("min_price", default=0.0, type=float)
    max_price = request.args.get("max_price", default=None, type=float)
    min_rating = request.args.get("min_rating", default=0.0, type=float)
    sort_by = request.args.get("sort_by", default="relevance")
    sort_order = request.args.get("sort_order", default="asc")
    limit = request.args.get("limit", default=24, type=int)
    offset = request.args.get("offset", default=0, type=int)

    # Record search history if user is logged in and query provided
    if query and "user_id" in session:
        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO search_history (user_id, search_query, searched_at) VALUES (?, ?, ?)",
                (session["user_id"], query.strip(), datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to record search history: {e}")

    result = get_products(
        query=query, category_id=category_id, platform_id=platform_id,
        min_price=min_price, max_price=max_price, min_rating=min_rating,
        sort_by=sort_by, sort_order=sort_order, limit=limit, offset=offset
    )
    return jsonify(result), 200


@app.route("/api/products/search", methods=["GET"])
def api_search_products():
    """Dedicated search endpoint matching prompt GET /api/products/search?q=earbuds."""
    query = request.args.get("q", "")
    result = get_products(query=query, limit=50)
    return jsonify(result), 200


@app.route("/api/products/<int:product_id>", methods=["GET"])
def api_get_product_detail(product_id: int):
    """Retrieves product details along with all platform offers."""
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product), 200


@app.route("/api/categories", methods=["GET"])
def api_get_categories():
    """Lists all 19 supported categories with icons and counts."""
    return jsonify(get_all_categories()), 200


@app.route("/api/platforms", methods=["GET"])
def api_get_platforms():
    """Lists all registered platforms and connection status."""
    return jsonify(get_all_platforms()), 200


@app.route("/api/offers/compare", methods=["GET"])
def api_compare_offers():
    """
    Compares offers for a single product across Amazon, Flipkart, Meesho, etc.
    Highlights the lowest verified total price (price + delivery).
    """
    product_id = request.args.get("product_id", type=int)
    if not product_id:
        return jsonify({"error": "product_id parameter is required"}), 400

    comparison = compare_product_platform_offers(product_id)
    if "error" in comparison:
        return jsonify(comparison), 404
    return jsonify(comparison), 200


@app.route("/api/products/compare-multiple", methods=["GET"])
def api_compare_multiple_products():
    """
    Compares 2 or more products side-by-side.
    Accepts: ?ids=1,2,3
    """
    ids_param = request.args.get("ids", "")
    try:
        product_ids = [int(x.strip()) for x in ids_param.split(",") if x.strip()]
    except ValueError:
        return jsonify({"error": "Invalid product IDs format. Use comma-separated integers."}), 400

    if not product_ids:
        return jsonify({"error": "Please provide at least one product ID."}), 400

    result = compare_products_side_by_side(product_ids)
    return jsonify(result), 200


@app.route("/api/products/budget", methods=["GET"])
def api_get_budget_products():
    """Endpoint matching prompt: GET /api/products/budget?min_price=500&max_price=3000."""
    min_price = request.args.get("min_price", default=0.0, type=float)
    max_price = request.args.get("max_price", default=None, type=float)
    result = get_products(min_price=min_price, max_price=max_price, limit=50)
    return jsonify(result), 200


@app.route("/api/products/sort", methods=["GET"])
def api_sort_products():
    """Endpoint matching prompt: GET /api/products/sort?by=price&order=asc."""
    sort_by = request.args.get("by", default="price")
    order = request.args.get("order", default="asc")
    result = get_products(sort_by=sort_by, sort_order=order, limit=50)
    return jsonify(result), 200


@app.route("/api/products/suggestions", methods=["GET"])
def api_search_suggestions():
    """Trie-powered auto-complete suggestion endpoint: GET /api/products/suggestions?q=blue."""
    q = request.args.get("q", "")
    suggestions = get_search_suggestions(q, limit=8)
    return jsonify({"query": q, "suggestions": suggestions}), 200


# -------------------------------------------------------------
# User Authentication Endpoints (Unit IV & V)
# -------------------------------------------------------------

@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters."}), 400
    if "@" not in email:
        return jsonify({"error": "A valid email address is required."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        password_hash = generate_password_hash(password)
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, is_admin, created_at) VALUES (?, ?, ?, 0, ?)",
            (username, email, password_hash, now_str)
        )
        conn.commit()
        user_id = cursor.lastrowid
        session["user_id"] = user_id
        session["username"] = username
        session["is_admin"] = False
        conn.close()

        logger.info(f"New user registered: {username} (ID: {user_id})")
        return jsonify({"message": "Registration successful!", "user": {"id": user_id, "username": username, "email": email}}), 201

    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Username or email is already registered."}), 409


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    username_or_email = data.get("username", "").strip()
    password = data.get("password", "")

    if not username_or_email or not password:
        return jsonify({"error": "Username and password are required."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM users WHERE username = ? OR email = ?
    """, (username_or_email, username_or_email))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user["password_hash"], password):
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["is_admin"] = bool(user["is_admin"])

        logger.info(f"User logged in: {user['username']}")
        return jsonify({
            "message": "Login successful!",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "is_admin": bool(user["is_admin"])
            }
        }), 200

    return jsonify({"error": "Invalid username or password."}), 401


@app.route("/api/auth/logout", methods=["POST", "GET"])
def api_logout():
    username = session.get("username", "Guest")
    session.clear()
    logger.info(f"User logged out: {username}")
    if request.path == "/api/auth/logout":
        return jsonify({"message": "Logged out successfully."}), 200
    return redirect(url_for("home_page"))


@app.route("/api/auth/me", methods=["GET"])
def api_get_current_user():
    if "user_id" in session:
        return jsonify({
            "logged_in": True,
            "user": {
                "id": session["user_id"],
                "username": session["username"],
                "is_admin": session.get("is_admin", False)
            }
        }), 200
    return jsonify({"logged_in": False, "user": None}), 200


# -------------------------------------------------------------
# Wishlist API Endpoints
# -------------------------------------------------------------

@app.route("/api/wishlist", methods=["GET"])
@login_required
def api_get_wishlist():
    user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT w.id as wishlist_id, w.created_at as saved_at,
               p.*, c.category_name,
               MIN(po.current_price) as min_price,
               MIN(po.current_price + po.delivery_charge) as min_total_cost,
               MAX(po.rating) as best_rating
        FROM wishlist w
        JOIN products p ON w.product_id = p.id
        JOIN categories c ON p.category_id = c.id
        LEFT JOIN product_offers po ON p.id = po.product_id
        WHERE w.user_id = ?
        GROUP BY w.id
        ORDER BY w.id DESC
    """, (user_id,))
    items = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({"wishlist": items, "count": len(items)}), 200


@app.route("/api/wishlist", methods=["POST"])
@login_required
def api_add_wishlist():
    data = request.get_json() or {}
    product_id = data.get("product_id")
    if not product_id:
        return jsonify({"error": "product_id is required"}), 400

    user_id = session["user_id"]
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO wishlist (user_id, product_id, created_at) VALUES (?, ?, ?)",
            (user_id, product_id, now_str)
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Product added to wishlist!", "product_id": product_id}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"message": "Product is already in your wishlist."}), 200


@app.route("/api/wishlist/<int:item_id>", methods=["DELETE"])
@login_required
def api_remove_wishlist(item_id: int):
    user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor()
    # Can delete by wishlist.id or product_id
    cursor.execute("DELETE FROM wishlist WHERE user_id = ? AND (id = ? OR product_id = ?)", (user_id, item_id, item_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()

    if affected > 0:
        return jsonify({"message": "Item removed from wishlist."}), 200
    return jsonify({"error": "Item not found in wishlist."}), 404


# -------------------------------------------------------------
# Search History Endpoints
# -------------------------------------------------------------

@app.route("/api/history", methods=["GET"])
def api_get_search_history():
    user_id = session.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor()

    if user_id:
        cursor.execute("""
            SELECT id, search_query, searched_at
            FROM search_history
            WHERE user_id = ?
            ORDER BY id DESC LIMIT 20
        """, (user_id,))
    else:
        cursor.execute("""
            SELECT id, search_query, searched_at
            FROM search_history
            ORDER BY id DESC LIMIT 10
        """)

    rows = cursor.fetchall()
    conn.close()
    return jsonify({"history": [dict(r) for r in rows]}), 200


@app.route("/api/history", methods=["DELETE"])
@login_required
def api_clear_search_history():
    user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM search_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Search history cleared successfully."}), 200


# -------------------------------------------------------------
# Price History and Price Alerts Endpoints
# -------------------------------------------------------------

@app.route("/api/price-history/<int:offer_id>", methods=["GET"])
def api_get_price_history(offer_id: int):
    """Retrieves chronological price changes for charting and trends."""
    data = get_offer_price_history(offer_id)
    return jsonify(data), 200


@app.route("/api/price-alerts", methods=["POST"])
@login_required
def api_create_price_alert():
    """Allows users to set target price alerts."""
    data = request.get_json() or {}
    offer_id = data.get("offer_id")
    target_price = data.get("target_price")

    if not offer_id or not target_price or float(target_price) <= 0:
        return jsonify({"error": "Valid offer_id and target_price are required."}), 400

    user_id = session["user_id"]
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO price_alerts (user_id, offer_id, target_price, is_active, created_at)
        VALUES (?, ?, ?, 1, ?)
    """, (user_id, offer_id, float(target_price), now_str))
    conn.commit()
    alert_id = cursor.lastrowid

    # Check if target is immediately met
    cursor.execute("SELECT current_price FROM product_offers WHERE id = ?", (offer_id,))
    row = cursor.fetchone()
    conn.close()

    triggered = False
    if row and row["current_price"] <= float(target_price):
        triggered = True

    return jsonify({
        "message": "Price alert created successfully!",
        "alert_id": alert_id,
        "is_immediately_active": triggered,
        "note": "Alerts trigger when updated prices meet your target budget."
    }), 201


@app.route("/api/price-alerts", methods=["GET"])
@login_required
def api_get_price_alerts():
    user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pa.*, po.current_price, pl.platform_name, p.product_name, p.image_url
        FROM price_alerts pa
        JOIN product_offers po ON pa.offer_id = po.id
        JOIN platforms pl ON po.platform_id = pl.id
        JOIN products p ON po.product_id = p.id
        WHERE pa.user_id = ?
        ORDER BY pa.id DESC
    """, (user_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({"alerts": rows}), 200


# -------------------------------------------------------------
# Admin Management Endpoints
# -------------------------------------------------------------

@app.route("/api/admin/products", methods=["GET"])
@admin_required
def api_admin_get_products():
    """Returns products for administration management."""
    result = get_products(limit=100)
    return jsonify(result), 200


@app.route("/api/admin/products", methods=["POST"])
@admin_required
def api_admin_create_product():
    """Adds a demonstration product to SQLite database."""
    data = request.get_json() or {}
    is_valid, err_msg = validate_product_data(data)
    if not is_valid:
        return jsonify({"error": err_msg}), 400

    new_id = create_product(data)
    return jsonify({"message": "Product created successfully!", "id": new_id}), 201


@app.route("/api/admin/products/<int:product_id>", methods=["PUT"])
@admin_required
def api_admin_update_product(product_id: int):
    """Updates product attributes."""
    data = request.get_json() or {}
    is_valid, err_msg = validate_product_data(data)
    if not is_valid:
        return jsonify({"error": err_msg}), 400

    success = update_product(product_id, data)
    if success:
        return jsonify({"message": "Product updated successfully!"}), 200
    return jsonify({"error": "Product not found or update failed."}), 404


@app.route("/api/admin/products/<int:product_id>", methods=["DELETE"])
@admin_required
def api_admin_delete_product(product_id: int):
    """Deletes product and its offers."""
    success = delete_product(product_id)
    if success:
        return jsonify({"message": "Product deleted successfully!"}), 200
    return jsonify({"error": "Product not found."}), 404


# -------------------------------------------------------------
# Unit V: Data Science, Pandas & DataFrames Analytics & Export
# -------------------------------------------------------------

@app.route("/api/admin/analytics", methods=["GET"])
@admin_required
def api_admin_analytics():
    """
    Demonstrates Unit V: Pandas and DataFrames
    Analyzes product catalog, computes summary statistics, average prices by category,
    and platform market shares.
    """
    conn = get_db_connection()
    # Read into Pandas DataFrame
    df_offers = pd.read_sql_query("""
        SELECT 
            p.id as product_id, p.product_name, p.brand, c.category_name,
            pl.platform_name, po.current_price, po.original_price,
            po.rating, po.delivery_charge
        FROM product_offers po
        JOIN products p ON po.product_id = p.id
        JOIN categories c ON p.category_id = c.id
        JOIN platforms pl ON po.platform_id = pl.id
    """, conn)
    conn.close()

    if df_offers.empty:
        return jsonify({"message": "No data available for analysis"}), 200

    # Calculate savings and discount percentage column in DataFrame
    df_offers["discount_pct"] = (
        (df_offers["original_price"] - df_offers["current_price"]) / df_offers["original_price"] * 100
    ).round(1)

    # 1. Category-wise Analysis DataFrame
    cat_summary = df_offers.groupby("category_name").agg(
        avg_price=("current_price", "mean"),
        min_price=("current_price", "min"),
        max_price=("current_price", "max"),
        avg_discount=("discount_pct", "mean"),
        total_offers=("product_id", "count")
    ).round(2).reset_index().to_dict(orient="records")

    # 2. Platform-wise Analysis DataFrame
    platform_summary = df_offers.groupby("platform_name").agg(
        avg_price=("current_price", "mean"),
        avg_rating=("rating", "mean"),
        avg_discount=("discount_pct", "mean"),
        offers_count=("product_id", "count")
    ).round(2).reset_index().to_dict(orient="records")

    # 3. Overall Statistics
    stats = {
        "total_records": int(len(df_offers)),
        "mean_price": float(round(df_offers["current_price"].mean(), 2)),
        "median_price": float(round(df_offers["current_price"].median(), 2)),
        "std_deviation_price": float(round(df_offers["current_price"].std(), 2)),
        "avg_discount_overall": float(round(df_offers["discount_pct"].mean(), 2)),
        "highest_discount": float(df_offers["discount_pct"].max())
    }

    return jsonify({
        "overall_statistics": stats,
        "category_analysis": cat_summary,
        "platform_analysis": platform_summary
    }), 200


@app.route("/api/admin/export", methods=["GET"])
@admin_required
def api_admin_export():
    """
    Demonstrates Unit V: Data Science Export (CSV, JSON, and XML).
    """
    export_format = request.args.get("format", "csv").lower()

    conn = get_db_connection()
    df = pd.read_sql_query("""
        SELECT 
            p.id, p.product_name, p.brand, c.category_name,
            pl.platform_name, po.current_price, po.original_price,
            po.rating, po.delivery_charge, po.last_updated
        FROM product_offers po
        JOIN products p ON po.product_id = p.id
        JOIN categories c ON p.category_id = c.id
        JOIN platforms pl ON po.platform_id = pl.id
    """, conn)
    conn.close()

    if export_format == "json":
        json_data = df.to_json(orient="records", indent=2)
        return Response(
            json_data,
            mimetype="application/json",
            headers={"Content-Disposition": "attachment;filename=shopfinder_export.json"}
        )

    elif export_format == "xml":
        root = ET.Element("ShopFinderCatalog")
        for _, row in df.iterrows():
            item_elem = ET.SubElement(root, "ProductOffer")
            for col in df.columns:
                sub = ET.SubElement(item_elem, str(col))
                sub.text = str(row[col])
        xml_str = ET.tostring(root, encoding="utf-8")
        return Response(
            xml_str,
            mimetype="application/xml",
            headers={"Content-Disposition": "attachment;filename=shopfinder_export.xml"}
        )

    else:
        # Default CSV export
        csv_data = df.to_csv(index=False)
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=shopfinder_export.csv"}
        )


# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "API route not found"}), 404
    return render_template("index.html", error_msg="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    if request.path.startswith("/api/"):
        return jsonify({"error": "Internal server error"}), 500
    return render_template("index.html", error_msg="Internal server error"), 500


if __name__ == "__main__":
    # Ensure database is created and seeded on initial run
    init_db()
    seed_data()
    init_search_trie()
    print("=" * 60)
    print(" ShopFinder Server Running on http://127.0.0.1:5000 ")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)
