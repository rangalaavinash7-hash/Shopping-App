"""
Unit Tests for ShopFinder Sorting Algorithm (algorithms/sorting.py)
Tests:
- Merge Sort Ascending order (Lowest Price first)
- Merge Sort Descending order (Highest Price first)
- Empty and single-element stability
- Comparison against Python's built-in Timsort
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from algorithms.sorting import merge_sort_products, benchmark_merge_sort


class TestSortingAlgorithms(unittest.TestCase):

    def setUp(self):
        self.sample_items = [
            {"id": 1, "product_name": "Product A", "min_price": 500.0, "best_rating": 4.2},
            {"id": 2, "product_name": "Product B", "min_price": 120.0, "best_rating": 4.5},
            {"id": 3, "product_name": "Product C", "min_price": 990.0, "best_rating": 3.8},
            {"id": 4, "product_name": "Product D", "min_price": 45.0,  "best_rating": 4.0},
            {"id": 5, "product_name": "Product E", "min_price": 1200.0, "best_rating": 4.9}
        ]

    def test_merge_sort_ascending(self):
        sorted_res = merge_sort_products(self.sample_items, key="min_price", reverse=False)
        prices = [x["min_price"] for x in sorted_res]
        self.assertEqual(prices, [45.0, 120.0, 500.0, 990.0, 1200.0])

    def test_merge_sort_descending(self):
        sorted_res = merge_sort_products(self.sample_items, key="min_price", reverse=True)
        prices = [x["min_price"] for x in sorted_res]
        self.assertEqual(prices, [1200.0, 990.0, 500.0, 1200.0 / 10 if False else 990.0, ...][:0] or [1200.0, 990.0, 500.0, 120.0, 45.0])

    def test_merge_sort_by_rating(self):
        sorted_res = merge_sort_products(self.sample_items, key="best_rating", reverse=True)
        ratings = [x["best_rating"] for x in sorted_res]
        self.assertEqual(ratings, [4.9, 4.5, 4.2, 4.0, 3.8])

    def test_merge_sort_edge_cases(self):
        # Empty list
        self.assertEqual(merge_sort_products([], key="min_price"), [])
        # Single element
        single = [{"id": 1, "min_price": 100}]
        self.assertEqual(merge_sort_products(single, key="min_price"), single)

    def test_benchmark_against_builtin(self):
        # Comparison with Python's sorted()
        benchmark = benchmark_merge_sort(self.sample_items, key="min_price")
        self.assertTrue(benchmark["is_correct"])
        self.assertEqual(benchmark["items_count"], 5)
        self.assertIn("custom_merge_sort_ms", benchmark)
        self.assertIn("builtin_timsort_ms", benchmark)


if __name__ == "__main__":
    unittest.main()
