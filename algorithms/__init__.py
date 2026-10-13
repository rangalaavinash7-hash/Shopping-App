"""
Algorithms & Data Structures Package for ShopFinder
Includes:
- search.py: Linear Search, Binary Search, and Trie Auto-completion
- sorting.py: Merge Sort (ascending/descending) with complexity benchmarks
- recommendations.py: Min-Heap / Priority Queue best-value recommendation engine
"""

from .search import linear_search_products, binary_search_by_price, SearchTrie
from .sorting import merge_sort_products, benchmark_merge_sort
from .recommendations import get_lowest_price_offers_heap, calculate_product_recommendation_score
