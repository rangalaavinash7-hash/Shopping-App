"""
ShopFinder Models (Unit IV: Object-Oriented Programming)
Defines classes: Product, ShoppingPlatform, ProductOffer, PriceTracker.
Demonstrates encapsulation, properties, dictionary serialization, and business logic.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List


class ShoppingPlatform:
    """
    Represents an external e-commerce shopping platform (e.g., Amazon, Flipkart, Meesho).
    """
    def __init__(self, platform_id: int, platform_name: str, website_url: str, 
                 integration_type: str = "DEMO", is_active: bool = True, logo_icon: str = ""):
        self.id = platform_id
        self.platform_name = platform_name
        self.website_url = website_url
        self.integration_type = integration_type  # 'DEMO', 'AFFILIATE_API', 'WEBHOOK'
        self.is_active = is_active
        self.logo_icon = logo_icon or platform_name.lower().replace(" ", "")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "platform_name": self.platform_name,
            "website_url": self.website_url,
            "integration_type": self.integration_type,
            "is_active": bool(self.is_active),
            "logo_icon": self.logo_icon
        }

    def __repr__(self) -> str:
        return f"<ShoppingPlatform(id={self.id}, name='{self.platform_name}')>"


class ProductOffer:
    """
    Represents a specific platform offer for a product, including current price,
    original price, delivery charge, rating, and platform link.
    """
    def __init__(self, offer_id: int, product_id: int, platform_id: int,
                 current_price: float, original_price: Optional[float] = None,
                 rating: float = 0.0, review_count: int = 0,
                 product_url: str = "#", delivery_charge: float = 0.0,
                 availability: str = "In Stock", data_source: str = "DEMONSTRATION",
                 last_updated: Optional[str] = None, platform_name: str = ""):
        self.id = offer_id
        self.product_id = product_id
        self.platform_id = platform_id
        self.current_price = float(current_price)
        self.original_price = float(original_price) if original_price else float(current_price)
        self.rating = float(rating)
        self.review_count = int(review_count)
        self.product_url = product_url
        self.delivery_charge = float(delivery_charge)
        self.availability = availability
        self.data_source = data_source
        self.last_updated = last_updated or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self.platform_name = platform_name

    @property
    def total_cost(self) -> float:
        """Calculates total price including delivery charges (Verified Total Price)."""
        return round(self.current_price + self.delivery_charge, 2)

    @property
    def discount_percentage(self) -> int:
        """Calculates percentage savings from original price (Unit I & II concepts)."""
        if self.original_price and self.original_price > self.current_price:
            savings = self.original_price - self.current_price
            return int(round((savings / self.original_price) * 100))
        return 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "product_id": self.product_id,
            "platform_id": self.platform_id,
            "platform_name": self.platform_name,
            "current_price": self.current_price,
            "original_price": self.original_price,
            "discount_percentage": self.discount_percentage,
            "total_cost": self.total_cost,
            "rating": self.rating,
            "review_count": self.review_count,
            "product_url": self.product_url,
            "delivery_charge": self.delivery_charge,
            "availability": self.availability,
            "data_source": self.data_source,
            "last_updated": self.last_updated
        }

    def __repr__(self) -> str:
        return f"<ProductOffer(id={self.id}, platform='{self.platform_name}', total={self.total_cost})>"


class Product:
    """
    Represents an overarching product across platforms with brand, model,
    category, and multiple offers for side-by-side comparison.
    """
    def __init__(self, product_id: int, product_name: str, brand: str,
                 category_id: int, category_name: str = "", model: str = "",
                 description: str = "", image_url: str = "", specifications: str = ""):
        self.id = product_id
        self.product_name = product_name
        self.brand = brand
        self.category_id = category_id
        self.category_name = category_name
        self.model = model
        self.description = description
        self.image_url = image_url
        self.specifications = specifications
        self.offers: List[ProductOffer] = []

    def add_offer(self, offer: ProductOffer):
        self.offers.append(offer)

    @property
    def lowest_offer(self) -> Optional[ProductOffer]:
        """Finds the offer with the lowest total price using Python's min function."""
        if not self.offers:
            return None
        return min(self.offers, key=lambda o: o.total_cost)

    @property
    def highest_offer(self) -> Optional[ProductOffer]:
        if not self.offers:
            return None
        return max(self.offers, key=lambda o: o.total_cost)

    @property
    def max_savings(self) -> float:
        """Maximum price difference between highest and lowest offer across platforms."""
        if len(self.offers) < 2:
            return 0.0
        return round(self.highest_offer.total_cost - self.lowest_offer.total_cost, 2)

    def to_dict(self, include_offers: bool = True) -> Dict[str, Any]:
        lowest = self.lowest_offer
        data = {
            "id": self.id,
            "product_name": self.product_name,
            "brand": self.brand,
            "model": self.model,
            "category_id": self.category_id,
            "category_name": self.category_name,
            "description": self.description,
            "image_url": self.image_url,
            "specifications": self.specifications,
            "offers_count": len(self.offers),
            "min_price": lowest.current_price if lowest else 0.0,
            "min_total_cost": lowest.total_cost if lowest else 0.0,
            "best_platform": lowest.platform_name if lowest else "",
            "best_discount": lowest.discount_percentage if lowest else 0,
            "best_rating": lowest.rating if lowest else 0.0,
            "max_savings": self.max_savings
        }
        if include_offers:
            data["offers"] = [offer.to_dict() for offer in self.offers]
        return data

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.product_name}', brand='{self.brand}')>"


class PriceTracker:
    """
    Tracks price history observations over time and evaluates target alerts.
    """
    def __init__(self, offer_id: int):
        self.offer_id = offer_id
        self.history_records: List[Dict[str, Any]] = []

    def record_price(self, price: float, timestamp: Optional[str] = None):
        rec = {
            "price": float(price),
            "timestamp": timestamp or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history_records.append(rec)

    def check_alert(self, current_price: float, target_price: float) -> bool:
        """Returns True if the current price is less than or equal to user target price."""
        return current_price <= target_price
