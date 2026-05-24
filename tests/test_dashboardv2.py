import unittest
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.product import Product
from app.models.product_size import ProductSize
from app.models.sale import Sale, SaleItem
from app.models.shop import Shop
from app.schemas.enums import SaleStatus
from app.services.dashboardv2 import DashboardV2Service


class TestDashboardV2Service(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
        self.db = TestingSessionLocal()
        self.service = DashboardV2Service()

        self.shop_1 = Shop(name="Shop 1", shop_code="S1")
        self.shop_2 = Shop(name="Shop 2", shop_code="S2")
        self.db.add_all([self.shop_1, self.shop_2])
        self.db.flush()

        product_1 = Product(name="Prod 1", unit_price=10, selling_price=20, shops=[self.shop_1, self.shop_2])
        product_1.size_map = [ProductSize(size="M", quantity=5)]

        product_2 = Product(name="Prod 2", unit_price=8, selling_price=12, shops=[self.shop_1])
        product_2.size_map = [ProductSize(size="M", quantity=0)]

        product_3 = Product(name="Prod 3", unit_price=6, selling_price=9, shops=[self.shop_2])
        product_3.size_map = [ProductSize(size="M", quantity=10)]
        self.db.add_all([product_1, product_2, product_3])
        self.db.flush()

        today = date.today().isoformat()
        sale_1 = Sale(
            date=today,
            total_quantity=3,
            total_price=60,
            shop_id=self.shop_1.id,
            status=SaleStatus.COMPLETED,
            sale_items=[
                SaleItem(
                    product_id=product_1.id,
                    product_name="Prod 1",
                    product_category="Cat",
                    size="M",
                    quantity=3,
                    quantity_available=10,
                    sale_price=20,
                    total_price=60,
                )
            ],
        )
        sale_2 = Sale(
            date=today,
            total_quantity=1,
            total_price=12,
            shop_id=self.shop_1.id,
            status=SaleStatus.COMPLETED,
            sale_items=[
                SaleItem(
                    product_id=product_2.id,
                    product_name="Prod 2",
                    product_category="Cat",
                    size="M",
                    quantity=1,
                    quantity_available=2,
                    sale_price=12,
                    total_price=12,
                )
            ],
        )
        sale_3 = Sale(
            date=today,
            total_quantity=2,
            total_price=18,
            shop_id=self.shop_2.id,
            status=SaleStatus.CANCELLED,
            sale_items=[
                SaleItem(
                    product_id=product_3.id,
                    product_name="Prod 3",
                    product_category="Cat",
                    size="M",
                    quantity=2,
                    quantity_available=20,
                    sale_price=9,
                    total_price=18,
                )
            ],
        )
        self.db.add_all([sale_1, sale_2, sale_3])
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_dashboardv2_all_shops_daily_metrics(self):
        result = self.service.get_dashboard_performance(
            db=self.db,
            period="daily",
            anchor_date=date.today().isoformat(),
        )

        metrics = result["metrics"]
        self.assertEqual(result["context"]["shop_name"], "All Shops")
        self.assertEqual(metrics["in_stock_summary"]["product_count"], 2)
        self.assertEqual(metrics["in_stock_summary"]["total_units"], 15)
        self.assertEqual(metrics["out_of_stock_summary"]["product_count"], 1)
        self.assertEqual(metrics["out_of_stock_summary"]["total_units"], 1)
        self.assertEqual(metrics["total_in_stock_value"], 110.0)
        self.assertEqual(metrics["expected_sales_value"], 190.0)
        self.assertEqual(metrics["expected_profit_loss"], 80.0)
        self.assertEqual(metrics["current_sales"], 72.0)
        self.assertEqual(metrics["current_profit_loss"], 34.0)
        self.assertEqual(metrics["most_sold_items"][0]["product_name"], "Prod 1")
        self.assertEqual(metrics["least_sold_items"][0]["product_name"], "Prod 2")

    def test_dashboardv2_shop_filter_metrics(self):
        result = self.service.get_dashboard_performance(
            db=self.db,
            period="daily",
            anchor_date=date.today().isoformat(),
            shop_id=self.shop_1.id,
        )

        metrics = result["metrics"]
        self.assertEqual(result["context"]["shop_name"], "Shop 1")
        self.assertEqual(metrics["in_stock_summary"]["product_count"], 1)
        self.assertEqual(metrics["in_stock_summary"]["total_units"], 5)
        self.assertEqual(metrics["out_of_stock_summary"]["product_count"], 1)
        self.assertEqual(metrics["out_of_stock_summary"]["total_units"], 1)
        self.assertEqual(metrics["total_in_stock_value"], 50.0)
        self.assertEqual(metrics["expected_sales_value"], 100.0)
        self.assertEqual(metrics["expected_profit_loss"], 50.0)
        self.assertEqual(metrics["current_sales"], 72.0)

    def test_dashboardv2_custom_range_validation(self):
        with self.assertRaises(ValueError):
            self.service.get_dashboard_performance(
                db=self.db,
                period="custom",
                start_date="2026-05-30",
                end_date="2026-05-01",
            )


if __name__ == "__main__":
    unittest.main()
