"""
Unit Tests for ShopFinder Search Algorithms (algorithms/search.py)
Tests:
- Linear Search (case-insensitive partial matching)
- Binary Search (logarithmic price lookup on sorted data)
- Trie Data Structure (prefix tree suggestions and autocomplete)
"""

import unittest
import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from algorithms.search import linear_search_products, binary_search_by_price, SearchTrie


class TestSearchAlgorithms(unittest.TestCase):

    def setUp(self):
        self.sample_products = [
            {"id": 1, "product_name": "boAt Airdopes 141", "brand": "boAt", "category_name": "Bluetooth Earbuds", "min_price": 1199},
            {"id": 2, "product_name": "OnePlus Nord Buds 2", "brand": "OnePlus", "category_name": "Bluetooth Earbuds", "min_price": 2499},
            {"id": 3, "product_name": "Apple iPhone 15", "brand": "Apple", "category_name": "Mobiles", "min_price": 64999},
            {"id": 4, "product_name": "Samsung Galaxy S24 Ultra", "brand": "Samsung", "category_name": "Mobiles", "min_price": 119999},
            {"id": 5, "product_name": "Sony MDR-ZX110A Headphones", "brand": "Sony", "category_name": "Headphones", "min_price": 799}
        ]

    def test_linear_search_found(self):
        # Case insensitive partial match
        results = linear_search_products(self.sample_products, "earbuds")
        self.assertEqual(len(results), 2)
        names = [r["product_name"] for r in results]
        self.assertIn("boAt Airdopes 141", names)
        self.assertIn("OnePlus Nord Buds 2", names)

    def test_linear_search_brand(self):
        results = linear_search_products(self.sample_products, "apple")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["brand"], "Apple")

    def test_linear_search_empty(self):
        # Empty query returns all products
        results = linear_search_products(self.sample_products, "")
        self.assertEqual(len(results), len(self.sample_products))

    def test_linear_search_no_match(self):
        results = linear_search_products(self.sample_products, "nonexistentgadgetxyz")
        self.assertEqual(len(results), 0)

    def test_binary_search_by_price(self):
        # Sorted list by min_price
        sorted_items = sorted(self.sample_products, key=lambda x: x["min_price"])
        
        # Exact match
        match = binary_search_by_price(sorted_items, 2499)
        self.assertIsNotNone(match)
        self.assertEqual(match["product_name"], "OnePlus Nord Buds 2")

        # Nearest match within tolerance
        match_near = binary_search_by_price(sorted_items, 1200, tolerance=50)
        self.assertIsNotNone(match_near)
        self.assertEqual(match_near["product_name"], "boAt Airdopes 141")

    def test_trie_autocomplete(self):
        trie = SearchTrie()
        trie.insert("iphone 15", {"title": "Apple iPhone 15"})
        trie.insert("iphone 14", {"title": "Apple iPhone 14"})
        trie.insert("ipad pro", {"title": "Apple iPad Pro"})
        trie.insert("boat airdopes", {"title": "boAt Airdopes 141"})

        # Prefix 'iph' should return both iPhones
        suggestions = trie.autocomplete("iph")
        self.assertEqual(len(suggestions), 2)
        titles = [s["title"] for s in suggestions]
        self.assertIn("Apple iPhone 15", titles)
        self.assertIn("Apple iPhone 14", titles)

        # Prefix 'bo'
        suggestions_bo = trie.autocomplete("bo")
        self.assertEqual(len(suggestions_bo), 1)
        self.assertEqual(suggestions_bo[0]["title"], "boAt Airdopes 141")

        # Non-matching prefix
        self.assertEqual(len(trie.autocomplete("xyz")), 0)


if __name__ == "__main__":
    unittest.main()
