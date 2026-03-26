import unittest
from unittest.mock import MagicMock, patch
from app.services.sale import SaleService
from app.services.day_management import DayManagementService
from app.services.customer import create_customer
from app.services.event import EventOfferService
from app.services.product import ProductService
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.schemas.day_management import DayCreate, ExpenseCreate
from app.schemas.customer import CustomerCreate
from app.schemas.event import EventOfferCreate
from app.schemas.product import ProductCreate
from app.models.sale import Sale
from app.models.day_management import Day, Expense
from app.models.customer import Customer
from app.models.event import EventOffer
from app.models.product import Product
from app.schemas.enums import SaleStatus
from app.models.event import RateType

class TestExtendedNotifications(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()

    @patch('app.services.sale.EmailNotificationService')
    def test_update_sale_status_sends_notification(self, MockEmailService):
        mock_email = MockEmailService.return_value
        service = SaleService()
        service.email_notification = mock_email

        sale = Sale(id=1, status=SaleStatus.COMPLETED, total_price=100.0, payment_type_id=1)
        sale.customer = MagicMock(name="Customer")
        service.get_sale = MagicMock(return_value=sale)

        service.update_sale_status(self.db, 1, "CANCELLED")

        mock_email.send_sale_status_change_notification.assert_called_once()

    @patch('app.services.day_management.EmailNotificationService')
    def test_start_day_sends_notification(self, MockEmailService):
        mock_email = MockEmailService.return_value
        service = DayManagementService()
        service.email_notification_service = mock_email

        # Mocking db calls to return a Day object
        self.db.query.return_value.filter.return_value.first.return_value = None # No day today
        service.get_active_day = MagicMock(return_value=None)

        day_create = DayCreate(opening_balance=1000.0)
        service.start_day(self.db, day_create)

        mock_email.send_day_start_notification.assert_called_once()

    @patch('app.services.day_management.EmailNotificationService')
    def test_add_expense_sends_notification(self, MockEmailService):
        mock_email = MockEmailService.return_value
        service = DayManagementService()
        service.email_notification_service = mock_email

        active_day = Day(id=1, opening_balance=1000.0)
        service.get_active_day = MagicMock(return_value=active_day)

        expense_create = ExpenseCreate(description="Test", amount=50.0, day_id=1)
        service.add_expense(self.db, expense_create)

        mock_email.send_expense_added_notification.assert_called_once()

    @patch('app.services.customer.EmailNotificationService')
    def test_create_customer_sends_notification(self, MockEmailService):
        from app.services import customer as customer_service
        # The instance is created at module level in customer.py
        with patch('app.services.customer.email_notification', MockEmailService.return_value) as mock_email:
            customer_create = CustomerCreate(name="New Customer", mobile="9876543210", email="new@example.com")
            customer_service.create_customer(self.db, customer_create)
            mock_email.send_customer_added_notification.assert_called_once()

    @patch('app.services.event.EmailNotificationService')
    def test_event_offer_notifications(self, MockEmailService):
        from datetime import datetime
        mock_email = MockEmailService.return_value
        service = EventOfferService()
        service.email_notification = mock_email

        offer_create = EventOfferCreate(
            name="Test Offer",
            code="TEST",
            type="category",
            is_active=True,
            rate=10,
            rate_type="percentage",
            product_ids=[],
            category_ids=[1],
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31)
        )
        service.apply_offer_to_products = MagicMock()

        # Create
        service.create_event_offer(self.db, offer_create)
        mock_email.send_offer_created_notification.assert_called_once()

        # Disable
        offer = EventOffer(id=1, name="Test", code="TEST")
        service.get_event_offer_by_id = MagicMock(return_value=offer)
        service.remove_offer_from_products = MagicMock()
        service.set_event_offer_active_status(self.db, 1, False)
        mock_email.send_offer_disabled_notification.assert_called_once()

    @patch('app.services.product.EmailNotificationService')
    def test_product_notifications(self, MockEmailService):
        mock_email = MockEmailService.return_value
        service = ProductService()
        service.email_notification = mock_email

        product_create = ProductCreate(
            name="New Product",
            unit_price=100,
            selling_price=150,
            category_id=1
        )
        # Add
        service.create_product(self.db, product_create)
        mock_email.send_product_added_notification.assert_called_once()

        # Delete
        product = Product(id=1, name="Deleted Product")
        service.get_product_by_id = MagicMock(return_value=product)
        service.delete_product(self.db, 1)
        mock_email.send_product_deleted_notification.assert_called_once()

        # Stock update
        mock_size = MagicMock()
        mock_size.quantity = 10
        self.db.query.return_value.filter.return_value.first.return_value = mock_size
        self.db.query.return_value.filter.return_value.first.side_effect = [mock_size, product]
        service.update_product_stock(self.db, 1, "M", 5)
        mock_email.send_product_stock_updated_notification.assert_called_once()

if __name__ == '__main__':
    unittest.main()
