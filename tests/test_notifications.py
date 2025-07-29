import unittest
from unittest.mock import MagicMock, patch
from app.services.sale import SaleService
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.models.sale import Sale

class TestNotifications(unittest.TestCase):
    @patch('app.services.notification.pywhatkit.sendwhatmsg_instantly')
    @patch('app.services.sale.EmailNotificationService')
    @patch('app.services.sale.ProductService')
    def test_create_sale_sends_notifications(self, MockProductService, MockEmailNotificationService, mock_sendwhatmsg_instantly):
        # Arrange
        db_session = MagicMock()
        mock_email_service = MockEmailNotificationService.return_value
        mock_product_service = MockProductService.return_value

        sale_create = SaleCreate(
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
        sale_service.create_sale(db_session, sale_create)

        # Assert
        mock_sendwhatmsg_instantly.assert_called_once_with(
            phone_no="+1234567890",
            message="Hi Test Customer, your sale with ID #None has been confirmed. Total amount: 100.0"
        )
        mock_email_service.send_sale_notification.assert_called_once()

if __name__ == '__main__':
    unittest.main()
