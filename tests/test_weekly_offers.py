import unittest
from unittest.mock import MagicMock, patch
from app.services.home import HomeService
from app.models.product import Product
from app.models.event import EventOffer

class TestWeeklyOffers(unittest.TestCase):

    def setUp(self):
        self.home_service = HomeService()
        self.db_session = MagicMock()

    @patch('app.services.event.EventOfferService.get_event_offer_by_code')
    @patch('app.services.home.HomeService._populate_product_images')
    def test_get_weekly_offers_found(self, mock_populate, mock_get_offer):
        # Arrange
        mock_product_1 = Product(id=1, name="Product 1")
        mock_product_2 = Product(id=2, name="Product 2")
        mock_offer = MagicMock(spec=EventOffer)
        mock_offer.products = [mock_product_1, mock_product_2]
        mock_get_offer.return_value = mock_offer

        # Act
        result = self.home_service.get_weekly_offers(self.db_session)

        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, "Product 1")
        self.assertEqual(result[1].name, "Product 2")
        mock_get_offer.assert_called_once_with(self.db_session, "WEEKLY50OFF")
        mock_populate.assert_called_once_with([mock_product_1, mock_product_2])

    @patch('app.services.event.EventOfferService.get_event_offer_by_code')
    def test_get_weekly_offers_not_found(self, mock_get_offer):
        # Arrange
        mock_get_offer.return_value = None

        # Act
        result = self.home_service.get_weekly_offers(self.db_session)

        # Assert
        self.assertEqual(len(result), 0)
        mock_get_offer.assert_called_once_with(self.db_session, "WEEKLY50OFF")

if __name__ == '__main__':
    unittest.main()
