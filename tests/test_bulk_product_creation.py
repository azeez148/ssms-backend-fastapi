import unittest
from unittest.mock import MagicMock, patch
from app.services.product import ProductService
from app.schemas.product import ProductCreate

class TestBulkProductCreation(unittest.TestCase):
    def setUp(self):
        self.product_service = ProductService()
        self.db = MagicMock()
        # Mocking the email notification service to avoid sending real emails
        self.product_service.email_notification = MagicMock()

    @patch('app.services.product.ProductService._create_product_instance')
    def test_create_bulk_products_success(self, mock_create_instance):
        # Setup mocks
        mock_p1 = MagicMock()
        mock_p2 = MagicMock()
        mock_create_instance.side_effect = [mock_p1, mock_p2]

        products_data = [
            ProductCreate(
                name="Product 1",
                unit_price=100,
                selling_price=150,
                category_id=1,
                is_active=True
            ),
            ProductCreate(
                name="Product 2",
                unit_price=200,
                selling_price=250,
                category_id=1,
                is_active=True
            )
        ]

        # Call the service method
        created_products = self.product_service.create_bulk_products(self.db, products_data)

        # Assertions
        self.assertEqual(len(created_products), 2)
        self.assertEqual(created_products[0], mock_p1)
        self.assertEqual(created_products[1], mock_p2)

        # Verify DB calls
        self.assertEqual(self.db.add.call_count, 2)
        self.db.commit.assert_called_once()
        self.assertEqual(self.db.refresh.call_count, 2)

        # Verify notification
        self.product_service.email_notification.send_bulk_product_added_notification.assert_called_once_with(created_products)

    def test_create_bulk_products_atomic_failure(self):
        products_data = [
            ProductCreate(
                name="Product 1",
                unit_price=100,
                selling_price=150,
                category_id=1
            )
        ]

        # Mock commit to raise an exception
        self.db.commit.side_effect = Exception("DB Error")

        with self.assertRaises(Exception):
            self.product_service.create_bulk_products(self.db, products_data)

        # Verify rollback was called
        self.db.rollback.assert_called_once()
        # Verify notification was NOT called
        self.product_service.email_notification.send_bulk_product_added_notification.assert_not_called()

if __name__ == "__main__":
    unittest.main()
