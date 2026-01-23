import unittest
from unittest.mock import MagicMock, patch
from app.services.sale import SaleService
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.models.sale import Sale, SaleItem
from app.schemas.enums import SaleStatus

class TestSales(unittest.TestCase):

    def setUp(self):
        self.sale_service = SaleService()
        self.db_session = MagicMock()

    @patch('app.services.sale.get_or_create_customer')
    @patch('app.services.sale.ProductService')
    @patch('app.services.sale.EmailNotificationService')
    def test_create_sale_with_sub_total(self, MockEmailService, MockProductService, MockGetCustomer):
        # Arrange
        MockGetCustomer.return_value = MagicMock(id=1)

        # Mock product size for stock update
        mock_product_size = MagicMock()
        mock_product_size.quantity = 10
        self.db_session.query.return_value.filter.return_value.first.return_value = mock_product_size

        sale_item = SaleItemCreate(
            product_id=1,
            product_name="Product 1",
            product_category="Category 1",
            size="M",
            quantity_available=10,
            quantity=2,
            sale_price=80.0,
            total_price=160.0
        )

        sale_create = SaleCreate(
            date="2025-08-15",
            total_quantity=2,
            sub_total=200.0, # 100 * 2
            total_price=160.0,
            payment_type_id=1,
            delivery_type_id=1,
            shop_id=1,
            customer_id=1,
            sale_items=[sale_item]
        )

        # Act
        db_sale = self.sale_service.create_sale(self.db_session, sale_create)

        # Assert
        self.assertEqual(db_sale.sub_total, 200.0)
        self.assertEqual(db_sale.total_price, 160.0)

    @patch('app.services.sale.get_or_create_customer')
    @patch('app.services.sale.ProductService')
    @patch('app.services.sale.EmailNotificationService')
    def test_create_sale_without_sub_total(self, MockEmailService, MockProductService, MockGetCustomer):
        # Arrange
        MockGetCustomer.return_value = MagicMock(id=1)

        # Mock product size for stock update
        mock_product_size = MagicMock()
        mock_product_size.quantity = 10
        self.db_session.query.return_value.filter.return_value.first.return_value = mock_product_size

        sale_item = SaleItemCreate(
            product_id=1,
            product_name="Product 1",
            product_category="Category 1",
            size="M",
            quantity_available=10,
            quantity=2,
            sale_price=80.0,
            total_price=160.0
        )

        # sub_total not provided (defaults to 0.0 in schema)
        sale_create = SaleCreate(
            date="2025-08-15",
            total_quantity=2,
            total_price=160.0,
            payment_type_id=1,
            delivery_type_id=1,
            shop_id=1,
            customer_id=1,
            sale_items=[sale_item]
        )

        # Act
        db_sale = self.sale_service.create_sale(self.db_session, sale_create)

        # Assert
        # Should default to total_price as per my change in SaleService
        self.assertEqual(db_sale.sub_total, 160.0)

if __name__ == '__main__':
    unittest.main()
