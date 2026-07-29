import unittest
from unittest.mock import MagicMock
from app.services.product import ProductService
from app.schemas.product import ProductHomeMinimalResponse

class TestHomeApiSizeMap(unittest.TestCase):
    def setUp(self):
        self.product_service = ProductService()
        self.db = MagicMock()

    def test_get_all_products_minimal_with_size_map(self):
        # Setup mock product with size map
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.name = "Test Product"
        mock_product.description = "Test Description"
        mock_product.unit_price = 100
        mock_product.selling_price = 150
        mock_product.category_id = 1
        mock_product.is_active = True
        mock_product.can_listed = True
        mock_product.image_url = "http://example.com/image.jpg"
        mock_product.is_duplicate = False
        mock_product.parent_product_id = None
        mock_product.discounted_price = 120
        mock_product.category.name = "Test Category"
        mock_product.shops = []
        mock_product.offer_id = None

        mock_size = MagicMock()
        mock_size.size = "M"
        mock_size.quantity = 10
        mock_product.size_map = [mock_size]

        # Mock the query results
        query = MagicMock()
        self.db.query.return_value = query

        order_query = MagicMock()
        query.order_by.return_value = order_query
        order_query.count.return_value = 1

        options_query = MagicMock()
        order_query.options.return_value = options_query

        offset_query = MagicMock()
        options_query.offset.return_value = offset_query

        offset_query.all.return_value = [mock_product]

        # Act
        products, total = self.product_service.get_all_products_minimal(self.db)

        # Assert
        self.assertEqual(len(products), 1)
        product = products[0]

        # Verify schema validation
        response_schema = ProductHomeMinimalResponse.model_validate(product)
        self.assertIsNotNone(response_schema.size_map)
        self.assertEqual(len(response_schema.size_map), 1)
        self.assertEqual(response_schema.size_map[0].size, "M")
        self.assertEqual(response_schema.size_map[0].quantity, 10)
        self.assertTrue(response_schema.is_in_stock)

if __name__ == "__main__":
    unittest.main()
