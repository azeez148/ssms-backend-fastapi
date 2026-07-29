import unittest
from unittest.mock import MagicMock, patch
from app.services.report import ReportService
from app.models.sale import Sale
from app.schemas.enums import SaleStatus
from app.schemas.report import SalesReportResponse

class TestReport(unittest.TestCase):
    def setUp(self):
        self.report_service = ReportService()
        self.db_session = MagicMock()

    def test_get_sales_report_logic(self):
        # Arrange
        sale1 = Sale(
            id=1,
            date="2023-10-01",
            total_price=100.0,
            total_quantity=2,
            status=SaleStatus.COMPLETED,
            payment_type_id=1,
            delivery_type_id=1,
            shop_id=1,
            sale_items=[]
        )
        sale2 = Sale(
            id=2,
            date="2023-10-02",
            total_price=200.0,
            total_quantity=3,
            status=SaleStatus.PENDING,
            payment_type_id=1,
            delivery_type_id=1,
            shop_id=1,
            sale_items=[]
        )
        sale3 = Sale(
            id=3,
            date="2023-10-05",
            total_price=150.0,
            total_quantity=1,
            status=SaleStatus.CANCELLED,
            payment_type_id=1,
            delivery_type_id=1,
            shop_id=1,
            sale_items=[]
        )

        # Mocking the query chain
        mock_query = self.db_session.query.return_value
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [sale1, sale2, sale3]

        # Act
        report = self.report_service.get_sales_report(self.db_session, "2023-10-01", "2023-10-31")

        # Assert
        self.assertEqual(report.total_sales, 3)
        self.assertEqual(report.total_amount, 450.0)
        self.assertEqual(report.total_quantity, 6)
        self.assertEqual(report.status_breakdown["COMPLETED"], 1)
        self.assertEqual(report.status_breakdown["PENDING"], 1)
        self.assertEqual(report.status_breakdown["CANCELLED"], 1)
        self.assertEqual(len(report.sales), 3)

    def test_get_sales_report_empty(self):
        # Arrange
        mock_query = self.db_session.query.return_value
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        report = self.report_service.get_sales_report(self.db_session, "2023-10-01", "2023-10-31")

        # Assert
        self.assertEqual(report.total_sales, 0)
        self.assertEqual(report.total_amount, 0.0)
        self.assertEqual(report.total_quantity, 0)
        self.assertEqual(report.status_breakdown, {})
        self.assertEqual(len(report.sales), 0)

    def test_get_sales_report_api(self):
        with patch("app.api.report.report_service.get_sales_report") as mock_get_report:
            mock_get_report.return_value = SalesReportResponse(
                sales=[],
                total_sales=0,
                status_breakdown={},
                total_amount=0.0,
                total_quantity=0
            )

            from fastapi.testclient import TestClient
            from app.main import app
            import os

            # Set SECRET_KEY if not set
            if "SECRET_KEY" not in os.environ:
                os.environ["SECRET_KEY"] = "test-secret-key"

            client = TestClient(app)

            response = client.get("/reports/sales?start_date=2023-10-01&end_date=2023-10-31")

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["total_sales"], 0)
            mock_get_report.assert_called_once()

if __name__ == '__main__':
    unittest.main()
