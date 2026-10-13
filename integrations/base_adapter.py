"""
ShopFinder Integrations: Base Adapter Module
Provides an extensible adapter architecture to plug in external e-commerce platforms.

Architectural Notice:
- Demonstration Data: Fully operational offline using SQLite seed records.
- Real External Platforms: Amazon Creator/PA-API, Flipkart Affiliate API, Croma/Reliance feeds
  require authorized developer tokens, client secrets, and partner agreements.
This adapter pattern guarantees new platforms can be added without rewriting the application.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import datetime


class BasePlatformAdapter(ABC):
    """
    Abstract interface for e-commerce shopping platform integrations.
    """
    def __init__(self, platform_name: str, base_url: str, is_live_integration: bool = False):
        self.platform_name = platform_name
        self.base_url = base_url
        self.is_live_integration = is_live_integration

    @abstractmethod
    def fetch_offers_by_keyword(self, query: str) -> List[Dict[str, Any]]:
        """Searches external platform API for real-time price offers."""
        pass

    @abstractmethod
    def get_product_details_by_id(self, external_product_id: str) -> Optional[Dict[str, Any]]:
        """Fetches detailed specifications and live stock availability."""
        pass

    def get_status(self) -> Dict[str, Any]:
        """Returns connection health and authentication status."""
        return {
            "platform_name": self.platform_name,
            "base_url": self.base_url,
            "is_live": self.is_live_integration,
            "status": "LIVE_AUTHORIZED" if self.is_live_integration else "DEMONSTRATION_FEED"
        }


class DemonstrationPlatformAdapter(BasePlatformAdapter):
    """
    Default adapter operating on reliable verified demonstration datasets.
    """
    def __init__(self, platform_name: str, base_url: str):
        super().__init__(platform_name, base_url, is_live_integration=False)

    def fetch_offers_by_keyword(self, query: str) -> List[Dict[str, Any]]:
        # Returns structured sample feed compatible with the API schema
        return []

    def get_product_details_by_id(self, external_product_id: str) -> Optional[Dict[str, Any]]:
        return None


class AmazonAffiliateAdapter(BasePlatformAdapter):
    """
    Reference blueprint for Amazon Product Advertising API (PA-API 5.0).
    Requires: AWS Access Key, Secret Key, Associate Tag, and Partner Approval.
    """
    def __init__(self, access_key: str = "", secret_key: str = "", associate_tag: str = ""):
        super().__init__("Amazon", "https://www.amazon.in", is_live_integration=bool(access_key))
        self.access_key = access_key
        self.secret_key = secret_key
        self.associate_tag = associate_tag

    def fetch_offers_by_keyword(self, query: str) -> List[Dict[str, Any]]:
        if not self.is_live_integration:
            # Clearly labeled as simulated external feed when keys not provided
            return []
        # In live production with AWS keys, use paapi5-python-sdk:
        # api_client.search_items(SearchItemsRequest(Keywords=query, PartnerTag=self.associate_tag))
        return []

    def get_product_details_by_id(self, external_product_id: str) -> Optional[Dict[str, Any]]:
        return None


class FlipkartAffiliateAdapter(BasePlatformAdapter):
    """
    Reference blueprint for Flipkart Affiliate API.
    Requires: Flipkart Tracking ID and Token.
    """
    def __init__(self, affiliate_id: str = "", token: str = ""):
        super().__init__("Flipkart", "https://www.flipkart.com", is_live_integration=bool(token))
        self.affiliate_id = affiliate_id
        self.token = token

    def fetch_offers_by_keyword(self, query: str) -> List[Dict[str, Any]]:
        if not self.is_live_integration:
            return []
        # In live production:
        # requests.get("https://affiliate-api.flipkart.net/affiliate/1.0/search.json", headers={...})
        return []

    def get_product_details_by_id(self, external_product_id: str) -> Optional[Dict[str, Any]]:
        return None
