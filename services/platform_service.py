"""
ShopFinder Platform Service
Manages shopping platforms (Amazon, Flipkart, Meesho, Myntra, etc.),
platform statistics, and adapter health status.
"""

from typing import List, Dict, Any, Optional
from database import get_db_connection
from integrations.base_adapter import DemonstrationPlatformAdapter, AmazonAffiliateAdapter, FlipkartAffiliateAdapter


def get_all_platforms() -> List[Dict[str, Any]]:
    """Retrieves all registered shopping platforms and their offer counts."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT pl.*, COUNT(po.id) AS offers_count,
               AVG(po.current_price) AS avg_price,
               AVG(po.rating) AS avg_rating
        FROM platforms pl
        LEFT JOIN product_offers po ON pl.id = po.platform_id
        GROUP BY pl.id
        ORDER BY pl.platform_name ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        item = dict(r)
        item["avg_price"] = round(item["avg_price"], 2) if item["avg_price"] else 0.0
        item["avg_rating"] = round(item["avg_rating"], 1) if item["avg_rating"] else 0.0
        # Determine adapter connectivity status
        item["integration_badge"] = "Verified Demonstration Data" if item["integration_type"] == "DEMO" else "Live API Feed"
        result.append(item)

    return result


def get_platform_adapter(platform_name: str):
    """Factory creating appropriate adapter instance."""
    name_lower = platform_name.lower()
    if "amazon" in name_lower:
        return AmazonAffiliateAdapter()
    elif "flipkart" in name_lower:
        return FlipkartAffiliateAdapter()
    else:
        return DemonstrationPlatformAdapter(platform_name, f"https://www.{name_lower}.com")
