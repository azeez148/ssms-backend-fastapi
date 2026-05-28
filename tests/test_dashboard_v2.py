import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch, call

from app.services.dashboard_v2 import (
    DashboardV2Service,
    _classify_category,
    _get_period_bounds,
    _total_revenue,
    _traffic,
    _compute_growth,
    _build_top_products,
    _build_traffic_heatmap,
    ACTIVE_STATUSES,
    STORE_PERFORMANCE_INDEX,
)
from app.schemas.enums import SaleStatus


def _make_sale(
    sale_id=1,
    date_str="2025-01-15",
    total_price=100.0,
    total_quantity=2,
    status=SaleStatus.COMPLETED,
    shop_id=1,
    customer_name="Alice",
    items=None,
):
    sale = MagicMock()
    sale.id = sale_id
    sale.date = date_str
    sale.total_price = total_price
    sale.total_quantity = total_quantity
    sale.status = status
    sale.shop_id = shop_id
    sale.payment_type_id = 1

    customer = MagicMock()
    customer.name = customer_name
    sale.customer = customer

    if items is None:
        item = MagicMock()
        item.product_name = "Air Max"
        item.product_category = "Footwear"
        item.quantity = 1
        item.total_price = total_price
        item.sale_price = total_price
        sale.sale_items = [item]
    else:
        sale.sale_items = items

    return sale


class TestClassifyCategory(unittest.TestCase):
    def test_footwear_keywords(self):
        self.assertEqual(_classify_category("Footwear"), "footwear")
        self.assertEqual(_classify_category("Running Shoes"), "footwear")
        self.assertEqual(_classify_category("Sneakers"), "footwear")

    def test_apparel_keywords(self):
        self.assertEqual(_classify_category("Apparel"), "apparel")
        self.assertEqual(_classify_category("Sports Jersey"), "apparel")
        self.assertEqual(_classify_category("Shorts"), "apparel")

    def test_other(self):
        self.assertEqual(_classify_category("Accessories"), "other")
        self.assertEqual(_classify_category(""), "other")
        self.assertEqual(_classify_category(None), "other")


class TestGetPeriodBounds(unittest.TestCase):
    def test_daily_bounds(self):
        start, end, prev_start, prev_end = _get_period_bounds("daily")
        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        self.assertEqual(start, today)
        self.assertEqual(end, today)
        self.assertEqual(prev_start, yesterday)
        self.assertEqual(prev_end, yesterday)

    def test_monthly_bounds(self):
        start, end, prev_start, prev_end = _get_period_bounds("monthly")
        today = date.today()
        self.assertEqual(start, today.replace(day=1).isoformat())
        self.assertTrue(end >= start)

    def test_yearly_bounds(self):
        start, end, prev_start, prev_end = _get_period_bounds("yearly")
        today = date.today()
        self.assertEqual(start, date(today.year, 1, 1).isoformat())
        self.assertEqual(end, date(today.year, 12, 31).isoformat())
        self.assertEqual(prev_start, date(today.year - 1, 1, 1).isoformat())
        self.assertEqual(prev_end, date(today.year - 1, 12, 31).isoformat())


class TestKpiHelpers(unittest.TestCase):
    def test_total_revenue_only_active(self):
        sales = [
            _make_sale(total_price=200.0, status=SaleStatus.COMPLETED),
            _make_sale(total_price=100.0, status=SaleStatus.CANCELLED),
            _make_sale(total_price=50.0, status=SaleStatus.SHIPPED),
        ]
        self.assertEqual(_total_revenue(sales), 250.0)

    def test_traffic_only_active(self):
        sales = [
            _make_sale(status=SaleStatus.COMPLETED),
            _make_sale(status=SaleStatus.CANCELLED),
            _make_sale(status=SaleStatus.SHIPPED),
            _make_sale(status=SaleStatus.PENDING),
        ]
        self.assertEqual(_traffic(sales), 2)

    def test_compute_growth_normal(self):
        self.assertEqual(_compute_growth(110.0, 100.0), 10.0)
        self.assertEqual(_compute_growth(90.0, 100.0), -10.0)

    def test_compute_growth_zero_previous(self):
        self.assertEqual(_compute_growth(100.0, 0.0), 0.0)


class TestBuildTopProducts(unittest.TestCase):
    def test_top_products_sorted_by_units(self):
        item_a = MagicMock()
        item_a.product_name = "Shoe A"
        item_a.quantity = 3
        item_a.total_price = 150.0

        item_b = MagicMock()
        item_b.product_name = "Jersey B"
        item_b.quantity = 10
        item_b.total_price = 200.0

        sales = [
            _make_sale(status=SaleStatus.COMPLETED, items=[item_a, item_b]),
        ]
        result = _build_top_products(sales)
        self.assertEqual(result[0].name, "Jersey B")
        self.assertEqual(result[0].units, 10)
        self.assertEqual(result[1].name, "Shoe A")
        self.assertEqual(result[1].units, 3)

    def test_cancelled_sales_excluded(self):
        item = MagicMock()
        item.product_name = "Cancelled Item"
        item.quantity = 5
        item.total_price = 100.0

        sales = [_make_sale(status=SaleStatus.CANCELLED, items=[item])]
        result = _build_top_products(sales)
        self.assertEqual(len(result), 0)


class TestBuildTrafficHeatmap(unittest.TestCase):
    def test_counts_by_weekday(self):
        # 2025-01-13 is a Monday
        sales = [
            _make_sale(date_str="2025-01-13", status=SaleStatus.COMPLETED),
            _make_sale(date_str="2025-01-13", status=SaleStatus.COMPLETED),
            _make_sale(date_str="2025-01-18", status=SaleStatus.COMPLETED),  # Saturday
        ]
        heatmap = _build_traffic_heatmap(sales)
        self.assertEqual(heatmap.Mon, 2)
        self.assertEqual(heatmap.Sat, 1)
        self.assertEqual(heatmap.Tue, 0)

    def test_cancelled_excluded_from_heatmap(self):
        sales = [
            _make_sale(date_str="2025-01-13", status=SaleStatus.CANCELLED),
        ]
        heatmap = _build_traffic_heatmap(sales)
        self.assertEqual(heatmap.Mon, 0)

    def test_invalid_date_skipped(self):
        sales = [
            _make_sale(date_str="not-a-date", status=SaleStatus.COMPLETED),
        ]
        heatmap = _build_traffic_heatmap(sales)
        total = heatmap.Mon + heatmap.Tue + heatmap.Wed + heatmap.Thu + heatmap.Fri + heatmap.Sat + heatmap.Sun
        self.assertEqual(total, 0)


class TestDashboardV2Service(unittest.TestCase):
    def setUp(self):
        self.service = DashboardV2Service()
        self.db = MagicMock()

    @patch("app.services.dashboard_v2._query_sales_in_period")
    def test_get_dashboard_data_structure(self, mock_query):
        mock_query.return_value = []
        result = self.service.get_dashboard_data(self.db, "daily")
        self.assertEqual(result.view, "daily")
        self.assertIsNotNone(result.kpi_stats)
        self.assertIsNotNone(result.branch_data)
        self.assertIsNotNone(result.top_products)
        self.assertIsNotNone(result.traffic_heatmap)

    @patch("app.services.dashboard_v2._query_sales_in_period")
    def test_get_dashboard_kpi_values(self, mock_query):
        sale = _make_sale(total_price=500.0, status=SaleStatus.COMPLETED, shop_id=1)
        mock_query.side_effect = [[sale], []]  # current, prev
        result = self.service.get_dashboard_data(self.db, "monthly")
        self.assertEqual(result.kpi_stats.total_revenue, 500.0)
        self.assertEqual(result.kpi_stats.traffic, 1)
        self.assertEqual(result.kpi_stats.avg_ticket_size, 500.0)
        self.assertEqual(result.kpi_stats.store_performance_index, STORE_PERFORMANCE_INDEX)

    @patch("app.services.dashboard_v2._query_sales_in_period")
    def test_view_variants_accepted(self, mock_query):
        mock_query.return_value = []
        for view in ("daily", "monthly", "yearly"):
            result = self.service.get_dashboard_data(self.db, view)
            self.assertEqual(result.view, view)


if __name__ == "__main__":
    unittest.main()
