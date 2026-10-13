"""
ShopFinder Comparison Service (Python Syllabus Units I, II & ADS)
Provides side-by-side product comparison, difference highlighting,
verified lowest price calculations, and price trend analysis.
"""

from typing import List, Dict, Any, Optional
from database import get_db_connection
from services.product_service import get_product_by_id, calculate_discount
from algorithms.recommendations import calculate_product_recommendation_score


def compare_products_side_by_side(product_ids: List[int]) -> Dict[str, Any]:
    """
    Compares two or more products side-by-side across brand, price,
    delivery, ratings, specs, and calculates the best-value recommendation.

    Telugu:
    రెండు లేదా అంతకంటే ఎక్కువ ప్రొడక్ట్ లను పక్కపక్కన పెట్టి ధరలు, ఫీచర్లు,
    డెలివరీ ఛార్జీలను పోల్చి చూపిస్తుంది.
    """
    if not product_ids:
        return {"products": [], "differences": [], "winner_product_id": None}

    products = []
    for pid in product_ids:
        p = get_product_by_id(pid)
        if p:
            # Score this product using recommendation algorithm
            p["recommendation_score"] = calculate_product_recommendation_score(p)
            products.append(p)

    if not products:
        return {"products": [], "differences": [], "winner_product_id": None}

    # Determine Winner by best recommendation score and lowest total cost
    winner = max(products, key=lambda x: (x["recommendation_score"], -x.get("min_total_cost", 999999)))

    # Compute difference flags (e.g. brand differences, price differences)
    differences = {
        "brands_differ": len(set(p["brand"] for p in products)) > 1,
        "categories_differ": len(set(p["category_id"] for p in products)) > 1,
        "price_gap": round(
            max(p.get("min_total_cost", 0) for p in products) - min(p.get("min_total_cost", 0) for p in products),
            2
        ) if len(products) > 1 else 0.0
    }

    return {
        "products": products,
        "differences": differences,
        "winner_product_id": winner["id"],
        "winner_name": winner["product_name"],
        "winner_reason": f"Highest Value-for-Money Score ({winner['recommendation_score']}/100) combining verified price, discount, and ratings."
    }


def compare_product_platform_offers(product_id: int) -> Dict[str, Any]:
    """
    Compares offers for a SINGLE product across all available e-commerce platforms.
    Highlights the lowest verified total price (current price + delivery charge).

    Telugu:
    ఒకే ప్రొడక్ట్ వివిధ షాపింగ్ ప్లాట్‌ఫారమ్‌లలో (Amazon, Flipkart, Meesho etc.)
    ఎంత ధరకు లభిస్తుందో స్పష్టంగా పోలుస్తుంది.
    """
    product = get_product_by_id(product_id)
    if not product:
        return {"error": "Product not found"}

    offers = product.get("offers", [])
    if not offers:
        return {"product": product, "offers": [], "best_deal": None}

    # Find the offer with minimum total cost (Price + Delivery)
    best_deal = min(offers, key=lambda o: o["total_cost"])
    highest_deal = max(offers, key=lambda o: o["total_cost"])
    total_savings = round(highest_deal["total_cost"] - best_deal["total_cost"], 2)

    return {
        "product_id": product["id"],
        "product_name": product["product_name"],
        "brand": product["brand"],
        "image_url": product["image_url"],
        "offers": offers,
        "best_deal": best_deal,
        "highest_deal": highest_deal,
        "total_savings": total_savings,
        "savings_percentage": round((total_savings / highest_deal["total_cost"] * 100), 1) if highest_deal["total_cost"] > 0 else 0
    }


def get_offer_price_history(offer_id: int) -> Dict[str, Any]:
    """
    Retrieves chronological price history observations for charting.
    Calculates whether the price has dropped or increased over time.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ph.recorded_price, ph.recorded_at, po.current_price, pl.platform_name, p.product_name
        FROM price_history ph
        JOIN product_offers po ON ph.offer_id = po.id
        JOIN platforms pl ON po.platform_id = pl.id
        JOIN products p ON po.product_id = p.id
        WHERE ph.offer_id = ?
        ORDER BY ph.recorded_at ASC
    """, (offer_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {"history": [], "trend": "STABLE", "price_change": 0.0}

    history = [dict(r) for r in rows]
    first_price = history[0]["recorded_price"]
    latest_price = history[-1]["recorded_price"]
    price_change = round(latest_price - first_price, 2)

    if price_change < 0:
        trend = "PRICE_DROP"
    elif price_change > 0:
        trend = "PRICE_INCREASE"
    else:
        trend = "STABLE"

    return {
        "offer_id": offer_id,
        "platform_name": rows[0]["platform_name"],
        "product_name": rows[0]["product_name"],
        "current_price": rows[0]["current_price"],
        "first_recorded_price": first_price,
        "latest_price": latest_price,
        "price_change": price_change,
        "trend": trend,
        "history": history
    }
