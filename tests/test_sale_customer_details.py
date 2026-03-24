import unittest
from unittest.mock import MagicMock, patch
from app.services.sale import SaleService
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.models.sale import Sale, SaleItem
from app.schemas.enums import SaleStatus

class TestSaleCustomerDetails(unittest.TestCase):

    def setUp(self):
        self.sale_service = SaleService()
        self.db_session = MagicMock()
        # Mocking db.add, db.flush, db.commit, db.refresh
        self.db_session.add = MagicMock()
        self.db_session.flush = MagicMock()
        self.db_session.commit = MagicMock()
        self.db_session.refresh = MagicMock()

    @patch('app.services.sale.get_or_create_customer')
    @patch('app.services.sale.ProductService')
    @patch('app.services.sale.EmailNotificationService')
    @patch('app.services.sale.DayManagementService')
    def test_create_sale_populates_customer_details_from_existing_customer(self, MockDayService, MockEmailService, MockProductService, MockGetCustomer):
        # Arrange
        mock_customer = MagicMock()
        mock_customer.id = 1
        mock_customer.first_name = "John"
        mock_customer.last_name = "Doe"
        mock_customer.name = "John Doe"
        mock_customer.address = "123 Main St"
        mock_customer.city = "New York"
        mock_customer.state = "NY"
        mock_customer.zip_code = "10001"
        mock_customer.mobile = "1234567890"
        mock_customer.email = "john@example.com"

        # Setup db.query(Customer).filter(...).first()
        self.db_session.query.return_value.filter.return_value.first.return_value = mock_customer

        # Mock product service update_product_stock to do nothing
        self.sale_service.product_service.update_product_stock = MagicMock()
        self.sale_service.day_management_service.update_day_from_sale = MagicMock()

        sale_item = SaleItemCreate(
            product_id=1,
            product_name="Product 1",
            product_category="Category 1",
            size="M",
            quantity_available=10,
            quantity=1,
            sale_price=100.0,
            total_price=100.0
        )

        sale_create = SaleCreate(
            date="2025-08-15",
            total_quantity=1,
            total_price=100.0,
            payment_type_id=1,
            delivery_type_id=1,
            shop_id=1,
            customer_id=1,
            sale_items=[sale_item]
        )

        # Act
        db_sale = self.sale_service.create_sale(self.db_session, sale_create)

        # Assert
        self.assertEqual(db_sale.customer_name, "John Doe")
        self.assertEqual(db_sale.customer_address, "123 Main St")
        self.assertEqual(db_sale.customer_city, "New York")
        self.assertEqual(db_sale.customer_state, "NY")
        self.assertEqual(db_sale.customer_zip_code, "10001")
        self.assertEqual(db_sale.customer_mobile, "1234567890")
        self.assertEqual(db_sale.customer_email, "john@example.com")

    @patch('app.services.sale.get_or_create_customer')
    @patch('app.services.sale.ProductService')
    @patch('app.services.sale.EmailNotificationService')
    @patch('app.services.sale.DayManagementService')
    def test_create_sale_prefers_provided_details_over_customer_object(self, MockDayService, MockEmailService, MockProductService, MockGetCustomer):
        # Arrange
        mock_customer = MagicMock()
        mock_customer.id = 1
        mock_customer.name = "John Doe"
        mock_customer.address = "123 Main St"
        mock_customer.mobile = "1234567890"

        self.db_session.query.return_value.filter.return_value.first.return_value = mock_customer

        # Mock services to do nothing
        self.sale_service.product_service.update_product_stock = MagicMock()
        self.sale_service.day_management_service.update_day_from_sale = MagicMock()

        sale_item = SaleItemCreate(
            product_id=1,
            product_name="Product 1",
            product_category="Category 1",
            size="M",
            quantity_available=10,
            quantity=1,
            sale_price=100.0,
            total_price=100.0
        )

        sale_create = SaleCreate(
            date="2025-08-15",
            total_quantity=1,
            total_price=100.0,
            payment_type_id=1,
            delivery_type_id=1,
            shop_id=1,
            customer_id=1,
            customer_name="Jane Smith",
            customer_address="456 Other St",
            sale_items=[sale_item]
        )

        # Act
        db_sale = self.sale_service.create_sale(self.db_session, sale_create)

        # Assert
        self.assertEqual(db_sale.customer_name, "Jane Smith")
        self.assertEqual(db_sale.customer_address, "456 Other St")
        self.assertEqual(db_sale.customer_mobile, "1234567890") # From customer object since not provided

if __name__ == '__main__':
    unittest.main()
