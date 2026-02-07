import unittest
from unittest.mock import MagicMock
from app.services.product import ProductService
from app.schemas.product import CategoryDiscountRequest
from app.models.category_discount import CategoryDiscount

class TestCategoryDiscounts(unittest.TestCase):

    def setUp(self):
        self.product_service = ProductService()
        self.db_session = MagicMock()

    def test_add_default_category_discounts_create(self):
        # Arrange
        request_data = CategoryDiscountRequest(category_ids=[1, 2], discounted_price=250)

        # Mock query to return None (no existing discounts)
        self.db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        results = self.product_service.add_default_category_discounts(self.db_session, request_data)

        # Assert
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].category_id, 1)
        self.assertEqual(results[0].discounted_price, 250)
        self.assertEqual(results[1].category_id, 2)
        self.assertEqual(results[1].discounted_price, 250)

        # Check if add was called twice
        self.assertEqual(self.db_session.add.call_count, 2)
        self.db_session.commit.assert_called_once()

    def test_add_default_category_discounts_update(self):
        # Arrange
        request_data = CategoryDiscountRequest(category_ids=[1], discounted_price=300)

        # Mock existing discount
        existing_discount = CategoryDiscount(id=1, category_id=1, discounted_price=250)
        self.db_session.query.return_value.filter.return_value.first.return_value = existing_discount

        # Act
        results = self.product_service.add_default_category_discounts(self.db_session, request_data)

        # Assert
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].discounted_price, 300)

        # Check if add was NOT called (it was an update)
        self.db_session.add.assert_not_called()
        self.db_session.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
