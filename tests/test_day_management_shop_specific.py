import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, date
from app.services.day_management import DayManagementService
from app.schemas.day_management import DayCreate, ExpenseCreate
from app.models.day_management import Day, Expense
from app.models.shop import Shop

class TestDayManagementShopSpecific(unittest.TestCase):

    def setUp(self):
        self.day_service = DayManagementService()
        self.db = MagicMock()

    def test_start_day_for_specific_shop(self):
        # Arrange
        shop_id = 2
        day_create = DayCreate(opening_balance=1000.0, shop_id=shop_id)

        # No day started today for this shop
        self.db.query.return_value.filter.return_value.first.return_value = None

        # Act
        db_day = self.day_service.start_day(self.db, day_create)

        # Assert
        self.assertEqual(db_day.shop_id, shop_id)
        self.assertEqual(db_day.opening_balance, 1000.0)
        self.db.add.assert_called()

    def test_get_active_day_per_shop(self):
        # Arrange
        shop_id = 3
        active_day = Day(id=10, shop_id=shop_id, end_time=None)

        # Mocking the query chain: db.query(Day).filter(Day.shop_id == shop_id, Day.end_time.is_(None)).first()
        self.db.query.return_value.filter.return_value.first.return_value = active_day

        # Act
        result = self.day_service.get_active_day(self.db, shop_id)

        # Assert
        self.assertEqual(result.id, 10)
        self.assertEqual(result.shop_id, shop_id)

    def test_add_expense_to_correct_shop_day(self):
        # Arrange
        shop_id = 1
        active_day = Day(id=1, shop_id=shop_id, total_expense=0.0, cash_in_hand=1000.0)
        expense_create = ExpenseCreate(description="Lunch", amount=50.0, day_id=1)

        self.db.query.return_value.filter.return_value.first.return_value = active_day

        # Act
        expense = self.day_service.add_expense(self.db, expense_create, shop_id=shop_id)

        # Assert
        self.assertEqual(active_day.total_expense, 50.0)
        self.assertEqual(active_day.cash_in_hand, 950.0)
        self.db.add.assert_called()

    def test_get_all_shops_status(self):
        # Arrange
        shop1 = Shop(id=1, name="Shop 1")
        shop2 = Shop(id=2, name="Shop 2")

        # Mock active day for shop 1, none for shop 2
        active_day1 = Day(id=101, shop_id=1)

        # We need to mock the db.query(Shop).all() call
        mock_query_shop = MagicMock()
        mock_query_shop.all.return_value = [shop1, shop2]

        # We also need to mock the db.query(Day).filter(...).first() call inside get_active_day
        mock_query_day = MagicMock()

        def db_query_side_effect(model):
            if model == Shop:
                return mock_query_shop
            return mock_query_day

        self.db.query.side_effect = db_query_side_effect

        # Actually it's easier to patch get_active_day
        with patch.object(self.day_service, 'get_active_day') as mock_get_active:
            mock_get_active.side_effect = lambda db, sid: active_day1 if sid == 1 else None

            # Act
            status = self.day_service.get_all_shops_status(self.db)

            # Assert
            self.assertEqual(len(status), 2)
            self.assertEqual(status[0]['shop_id'], 1)
            self.assertTrue(status[0]['day_started'])
            self.assertEqual(status[1]['shop_id'], 2)
            self.assertFalse(status[1]['day_started'])

if __name__ == '__main__':
    unittest.main()
