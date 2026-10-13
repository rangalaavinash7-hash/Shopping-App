"""
Unit and Integration Tests for ShopFinder Flask REST API
Tests all key endpoints, input validation, authentication, and algorithm integrations.
"""

import unittest
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from database import init_db, seed_data


class TestShopFinderAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        seed_data()

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check(self):
        res = self.app.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "healthy")

    def test_get_categories(self):
        res = self.app.get("/api/categories")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 15)

    def test_get_platforms(self):
        res = self.app.get("/api/platforms")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIsInstance(data, list)
        platform_names = [p["platform_name"] for p in data]
        self.assertIn("Amazon", platform_names)
        self.assertIn("Flipkart", platform_names)

    def test_product_search(self):
        res = self.app.get("/api/products/search?q=earbuds")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("products", data)
        self.assertGreater(data["total_count"], 0)

    def test_budget_filter(self):
        res = self.app.get("/api/products/budget?min_price=500&max_price=3000")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        for p in data["products"]:
            self.assertGreaterEqual(p["min_price"], 500)
            self.assertLessEqual(p["min_price"], 3000)

    def test_sort_endpoint(self):
        res = self.app.get("/api/products/sort?by=price&order=asc")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        prices = [p["min_price"] for p in data["products"]]
        self.assertEqual(prices, sorted(prices))

    def test_trie_suggestions(self):
        res = self.app.get("/api/products/suggestions?q=boat")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("suggestions", data)

    def test_compare_offers(self):
        res = self.app.get("/api/offers/compare?product_id=1")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("offers", data)
        self.assertIn("best_deal", data)
        self.assertIn("total_savings", data)

    def test_user_login_demo(self):
        res = self.app.post("/api/auth/login", json={
            "username": "shopper",
            "password": "shop123"
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["user"]["username"], "shopper")

    def test_invalid_login(self):
        res = self.app.post("/api/auth/login", json={
            "username": "shopper",
            "password": "wrongpassword"
        })
        self.assertEqual(res.status_code, 401)


if __name__ == "__main__":
    unittest.main()
