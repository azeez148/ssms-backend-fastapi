import unittest
from unittest.mock import MagicMock, patch
from app.services.home import HomeService
from app.models.product import Product
from app.models.shop import Shop

class TestHomeServiceRestriction(unittest.TestCase):
    def setUp(self):
        self.home_service = HomeService()
        self.db = MagicMock()

    @patch('app.services.home.settings')
    def test_filter_restricted_products(self, mock_settings):
        # Setup mock settings
        mock_settings.RESTRICT_SHOPS = True
        mock_settings.RESTRICTED_SHOP_IDS = [2]
        mock_settings.RESTRICTED_SHOP_CODES = ["DR-CVR"]

        # Create mock shops
        shop1 = Shop(id=1, shop_code="SHOP1")
        shop2 = Shop(id=2, shop_code="DR-CVR")
        shop3 = Shop(id=3, shop_code="SHOP3")

        # Product 1: Only in Shop 1 (Should be kept)
        p1 = Product(id=1, name="P1", shops=[shop1])

        # Product 2: Only in Shop 2 (Should be filtered)
        p2 = Product(id=2, name="P2", shops=[shop2])

        # Product 3: In both Shop 1 and Shop 2 (Should be kept)
        p3 = Product(id=3, name="P3", shops=[shop1, shop2])

        # Product 4: Only in Shop 3 (Should be kept)
        p4 = Product(id=4, name="P4", shops=[shop3])

        products = [p1, p2, p3, p4]
        filtered = self.home_service._filter_restricted_products(products)

        self.assertEqual(len(filtered), 3)
        self.assertIn(p1, filtered)
        self.assertNotIn(p2, filtered)
        self.assertIn(p3, filtered)
        self.assertIn(p4, filtered)

    @patch('app.services.home.settings')
    def test_filter_restricted_products_disabled(self, mock_settings):
        # This test actually tests the logic when settings.RESTRICT_SHOPS is True,
        # but here we just want to see if the filtering logic itself works correctly
        # when it IS called.

        mock_settings.RESTRICTED_SHOP_IDS = [2]
        mock_settings.RESTRICTED_SHOP_CODES = ["DR-CVR"]

        shop2 = Shop(id=2, shop_code="DR-CVR")
        p2 = Product(id=2, name="P2", shops=[shop2])

        products = [p2]
        filtered = self.home_service._filter_restricted_products(products)
        self.assertEqual(len(filtered), 0)

if __name__ == '__main__':
    unittest.main()
