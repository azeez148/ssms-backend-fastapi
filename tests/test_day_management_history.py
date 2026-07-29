import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, date
from app.services.day_management import DayManagementService
from app.models.day_management import Day, Expense
from app.models.shop import Shop

class TestDayManagementHistory(unittest.TestCase):

    def setUp(self):
        self.day_service = DayManagementService()
        self.db = MagicMock()

    def test_get_days_range(self):
        # Arrange
        start_date = "2023-01-01"
        end_date = "2023-01-10"
        shop_id = 1

        shop = Shop(id=shop_id, name="Test Shop")
        day1 = Day(id=1, shop_id=shop_id, start_time=datetime(2023, 1, 1, 10, 0), end_time=datetime(2023, 1, 1, 20, 0), opening_balance=100.0, shop=shop)
        day2 = Day(id=2, shop_id=shop_id, start_time=datetime(2023, 1, 2, 10, 0), end_time=None, opening_balance=200.0, shop=shop)

        mock_query = self.db.query.return_value.filter.return_value.filter.return_value.order_by.return_value
        mock_query.all.return_value = [day2, day1]

        # Mocking _populate_live_totals to avoid actual DB calls for live data
        with patch.object(self.day_service, '_populate_live_totals') as mock_populate:
            with patch.object(self.day_service, 'get_expenses_for_day') as mock_expenses:
                mock_expenses.return_value = []

                # Act
                results = self.day_service.get_days_range(self.db, start_date, end_date, shop_id)

                # Assert
                self.assertEqual(len(results), 2)
                self.assertEqual(results[0].day_id, 2)
                self.assertEqual(results[1].day_id, 1)
                self.assertTrue(results[0].day_started)
                self.assertFalse(results[0].day_ended)
                self.assertTrue(results[1].day_ended)
                mock_populate.assert_called_once_with(self.db, day2)

if __name__ == '__main__':
    unittest.main()
