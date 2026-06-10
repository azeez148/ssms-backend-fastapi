import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.sale import Sale
from app.schemas.enums import SaleStatus
from app.services.sale import SaleService

class TestSaleOrdering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use SQLite for testing
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.db = self.SessionLocal()
        self.sale_service = SaleService()
        # Clean up sales table before each test
        self.db.query(Sale).delete()
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_get_all_sales_default_ordering(self):
        # Create sales in mixed order of ID and status
        # IDs will be assigned automatically by SQLite starting from 1
        sales_to_create = [
            Sale(id=1, date="2023-01-01", total_quantity=1, total_price=10.0, payment_type_id=1, delivery_type_id=1, shop_id=1, status=SaleStatus.COMPLETED),
            Sale(id=2, date="2023-01-02", total_quantity=1, total_price=20.0, payment_type_id=1, delivery_type_id=1, shop_id=1, status=SaleStatus.PENDING),
            Sale(id=3, date="2023-01-03", total_quantity=1, total_price=30.0, payment_type_id=1, delivery_type_id=1, shop_id=1, status=SaleStatus.SHIPPED),
            Sale(id=4, date="2023-01-04", total_quantity=1, total_price=40.0, payment_type_id=1, delivery_type_id=1, shop_id=1, status=SaleStatus.PENDING),
            Sale(id=5, date="2023-01-05", total_quantity=1, total_price=50.0, payment_type_id=1, delivery_type_id=1, shop_id=1, status=SaleStatus.CANCELLED),
        ]
        self.db.add_all(sales_to_create)
        self.db.commit()

        # NEW BEHAVIOR: PENDING first, then by ID descending
        # Pending IDs are 4 and 2. 4 > 2, so [4, 2]
        # Remaining IDs are 5, 3, 1. Sorted desc: [5, 3, 1]
        # Total expected: [4, 2, 5, 3, 1]
        sales, total = self.sale_service.get_all_sales(self.db)
        ids = [s.id for s in sales]
        statuses = [s.status for s in sales]
        print(f"New ordering ids: {ids}")
        print(f"New ordering statuses: {statuses}")
        self.assertEqual(ids, [4, 2, 5, 3, 1])
        self.assertEqual(statuses[0], SaleStatus.PENDING)
        self.assertEqual(statuses[1], SaleStatus.PENDING)

    def test_get_all_sales_with_status_filter(self):
        sales_to_create = [
            Sale(id=1, date="2023-01-01", total_quantity=1, total_price=10.0, payment_type_id=1, delivery_type_id=1, shop_id=1, status=SaleStatus.COMPLETED),
            Sale(id=2, date="2023-01-02", total_quantity=1, total_price=20.0, payment_type_id=1, delivery_type_id=1, shop_id=1, status=SaleStatus.PENDING),
            Sale(id=3, date="2023-01-03", total_quantity=1, total_price=30.0, payment_type_id=1, delivery_type_id=1, shop_id=1, status=SaleStatus.COMPLETED),
        ]
        self.db.add_all(sales_to_create)
        self.db.commit()

        sales, total = self.sale_service.get_all_sales(self.db, status=SaleStatus.COMPLETED)
        ids = [s.id for s in sales]
        self.assertEqual(ids, [3, 1])
        self.assertEqual(total, 2)

if __name__ == "__main__":
    unittest.main()
