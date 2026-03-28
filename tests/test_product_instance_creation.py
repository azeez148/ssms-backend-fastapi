import unittest
from unittest.mock import MagicMock, patch
from app.services.product import ProductService
from app.schemas.product import ProductCreate
from app.models.product import Product
from app.models.shop import Shop

class TestProductInstanceCreation(unittest.TestCase):
    def setUp(self):
        self.product_service = ProductService()
        self.db = MagicMock()

    def test_create_product_instance_default_shop(self):
        # Setup mock for Shop ID 1
        mock_shop = MagicMock()
        mock_shop.id = 1
        # Mocking the query to return our mock shop
        self.db.query().filter().first.return_value = mock_shop

        product_data = ProductCreate(
            name="Test Product",
            unit_price=100,
            selling_price=150,
            category_id=1
        )

        # Call the private method (using _ to access it)
        with patch('app.services.product.Product', spec=Product) as MockProduct:
            mock_product_instance = MagicMock()
            mock_product_instance.shops = []
            mock_product_instance.size_map = []
            MockProduct.return_value = mock_product_instance

            instance = self.product_service._create_product_instance(self.db, product_data)

            # Check if shop 1 was added
            self.assertIn(mock_shop, instance.shops)
            # Verify the constructor was called with correct data
            MockProduct.assert_called_once()
            args, kwargs = MockProduct.call_args
            self.assertEqual(kwargs['name'], "Test Product")

    def test_create_product_instance_specific_shops(self):
        # Setup mock for Shops
        mock_shop_2 = MagicMock()
        mock_shop_2.id = 2
        mock_shop_3 = MagicMock()
        mock_shop_3.id = 3

        self.db.query().filter().all.return_value = [mock_shop_2, mock_shop_3]

        product_data = ProductCreate(
            name="Test Product",
            unit_price=100,
            selling_price=150,
            category_id=1,
            shop_ids=[2, 3]
        )

        with patch('app.services.product.Product', spec=Product) as MockProduct:
            mock_product_instance = MagicMock()
            mock_product_instance.shops = []
            mock_product_instance.size_map = []
            MockProduct.return_value = mock_product_instance

            instance = self.product_service._create_product_instance(self.db, product_data)

            # Check if specific shops were set
            self.assertEqual(instance.shops, [mock_shop_2, mock_shop_3])

if __name__ == "__main__":
    unittest.main()
