from .product_service import (
    get_products,
    get_product_by_id,
    get_all_categories,
    get_all_brands,
    get_search_suggestions,
    create_product,
    update_product,
    delete_product,
    filter_by_budget,
    sort_products_by_price,
    calculate_discount,
    validate_product_data
)
from .comparison_service import (
    compare_products_side_by_side,
    compare_product_platform_offers,
    get_offer_price_history
)
from .platform_service import (
    get_all_platforms,
    get_platform_adapter
)
