import unittest
from unittest.mock import MagicMock, patch
import sys
sys.modules['pywhatkit'] = MagicMock()
from app.services.sale import SaleService
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.models.sale import Sale

class TestNotifications(unittest.TestCase):
    @patch('app.services.sale.get_or_create_customer')
    @patch('app.services.notification.pywhatkit.sendwhatmsg_instantly')
    @patch('app.services.sale.EmailNotificationService')
    @patch('app.services.sale.ProductService')
    def test_create_sale_sends_notifications(self, MockProductService, MockEmailNotificationService, mock_sendwhatmsg_instantly, mock_get_or_create_customer):
        # Arrange
        db_session = MagicMock()
        mock_email_service = MockEmailNotificationService.return_value
        mock_product_service = MockProductService.return_value

        # Mock customer
        mock_customer = MagicMock()
        mock_customer.id = 123
        mock_customer.name = "Test Customer"
        mock_customer.mobile = "+1234567890"
        mock_customer.email = "test@example.com"
        mock_get_or_create_customer.return_value = mock_customer

        def mock_refresh(obj):
            if isinstance(obj, Sale):
                obj.customer = mock_customer
        db_session.refresh.side_effect = mock_refresh

        sale_create = SaleCreate(
            customer_id=0, # new customer
            customer_name="Test Customer",
            customer_address="123 Test St",
            customer_mobile="+1234567890",
            customer_email="test@example.com",
            date="2025-07-29",
            total_quantity=1,
            total_price=100.0,
            payment_type_id=1,
            delivery_type_id=1,
            shop_id=1,
            sale_items=[
                SaleItemCreate(
                    product_id=1,
                    product_name="Test Product",
                    product_category="Test Category",
                    size="M",
                    quantity_available=10,
                    quantity=1,
                    sale_price=100.0,
                    total_price=100.0
                )
            ]
        )

        sale_service = SaleService()
        sale_service.email_notification = mock_email_service
        sale_service.product_service = mock_product_service

        # Act
        created_sale = sale_service.create_sale(db_session, sale_create)

        # Assert
        # The sale object passed to the notification service should have a customer
        mock_email_service.send_sale_notification.assert_called_once()
        sent_sale = mock_email_service.send_sale_notification.call_args[0][0]
        self.assertEqual(sent_sale.customer.name, "Test Customer")

        # The whatsapp notification should also be called with the correct details
        mock_sendwhatmsg_instantly.assert_called_once()
        self.assertIn("Hi Test Customer", mock_sendwhatmsg_instantly.call_args[1]['message'])

if __name__ == '__main__':
    unittest.main()
