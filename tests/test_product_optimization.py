import unittest
from unittest.mock import MagicMock, patch
from app.models.product import Product
from app.services.product import ProductService

class TestProductOptimization(unittest.TestCase):
    def setUp(self):
        self.product_service = ProductService()
        self.db = MagicMock()

    def test_get_all_products_paginated(self):
        query = MagicMock()
        options_query = MagicMock()
        offset_query = MagicMock()
        limit_query = MagicMock()

        self.db.query.return_value = query
        query.count.return_value = 100
        query.options.return_value = options_query
        options_query.offset.return_value = offset_query
        offset_query.limit.return_value = limit_query
        limit_query.all.return_value = []

        # Act
        items, total = self.product_service.get_all_products(self.db, skip=10, limit=20)

        # Assert
        self.assertEqual(total, 100)
        options_query.offset.assert_called_once_with(10)
        offset_query.limit.assert_called_once_with(20)

    def test_get_all_products_filtering(self):
        query = MagicMock()
        self.db.query.return_value = query
        filter_query = MagicMock()
        query.filter.return_value = filter_query
        filter_query.filter.return_value = filter_query
        filter_query.count.return_value = 10

        options_query = MagicMock()
        filter_query.options.return_value = options_query
        offset_query = MagicMock()
        options_query.offset.return_value = offset_query
        offset_query.all.return_value = []

        # Act
        items, total = self.product_service.get_all_products(self.db, category_id=1, shop_id=2)

        # Assert
        self.assertEqual(total, 10)
        # Two filter calls expected: one for category_id, one for shops.any
        self.assertEqual(query.filter.call_count + filter_query.filter.call_count, 2)

    def test_get_all_products_search(self):
        query = MagicMock()
        self.db.query.return_value = query
        filter_query = MagicMock()
        query.filter.return_value = filter_query
        filter_query.count.return_value = 5

        options_query = MagicMock()
        filter_query.options.return_value = options_query
        offset_query = MagicMock()
        options_query.offset.return_value = offset_query
        offset_query.all.return_value = []

        # Act
        items, total = self.product_service.get_all_products(self.db, search="test")

        # Assert
        self.assertEqual(total, 5)
        query.filter.assert_called_once()

    def test_get_all_products_minimal(self):
        query = MagicMock()
        self.db.query.return_value = query
        query.count.return_value = 1
        options_query = MagicMock()
        query.options.return_value = options_query
        offset_query = MagicMock()
        options_query.offset.return_value = offset_query

        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.name = "Test"
        mock_product.description = "Desc"
        mock_product.unit_price = 100
        mock_product.selling_price = 150
        mock_product.category_id = 1
        mock_product.is_active = True
        mock_product.can_listed = True
        mock_product.image_url = "url"
        mock_product.discounted_price = None
        mock_product.category.name = "Cat"
        mock_shop = MagicMock()
        mock_shop.id = 1
        mock_shop.name = "Shop"
        mock_shop.shop_code = "S1"
        mock_product.shops = [mock_shop]

        offset_query.all.return_value = [mock_product]

        # Act
        items, total = self.product_service.get_all_products_minimal(self.db)

        # Assert
        self.assertEqual(total, 1)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].name, "Test")
        self.assertEqual(items[0].category_name, "Cat")
        self.assertEqual(items[0].shops[0].name, "Shop")

if __name__ == "__main__":
    unittest.main()
