import unittest
from unittest.mock import MagicMock, patch
from app.services.event import EventOfferService
from app.models.product import Product
from app.models.event import EventOffer, RateType

class TestOffers(unittest.TestCase):

    def setUp(self):
        self.event_offer_service = EventOfferService()
        self.db_session = MagicMock()

    def test_update_product_offer_apply(self):
        # Arrange
        mock_product_1 = Product(id=1, name="Product 1", selling_price=100, offer_id=None)
        mock_product_2 = Product(id=2, name="Product 2", selling_price=200, offer_id=10, offer_name="Old Offer")

        mock_old_offer = EventOffer(id=10, name="Old Offer", product_ids="2")
        mock_new_offer = EventOffer(id=1, name="New Offer", rate_type=RateType.flat, rate=10, product_ids="")

        mock_query_product = MagicMock()
        mock_query_product.filter.return_value.all.return_value = [mock_product_1, mock_product_2]

        mock_query_offer = MagicMock()
        mock_query_offer.filter.return_value.first.side_effect = [mock_new_offer, mock_old_offer, mock_new_offer]

        def db_query_side_effect(model):
            if model == Product:
                return mock_query_product
            if model == EventOffer:
                return mock_query_offer
            return MagicMock()

        self.db_session.query.side_effect = db_query_side_effect

        # Act
        result = self.event_offer_service.update_product_offer(self.db_session, [1, 2], 1)

        # Assert
        self.assertEqual(result["updated_count"], 2)
        self.assertEqual(mock_product_1.offer_id, 1)
        self.assertEqual(mock_product_1.discounted_price, 90)
        self.assertEqual(mock_product_2.offer_id, 1)
        self.assertEqual(mock_product_2.discounted_price, 190)

        # Check product_ids strings
        self.assertEqual(mock_old_offer.product_ids, "")
        pids = mock_new_offer.product_ids.split(",")
        self.assertIn("1", pids)
        self.assertIn("2", pids)

    def test_update_product_offer_remove(self):
        # Arrange
        mock_product_2 = Product(id=2, name="Product 2", selling_price=200, offer_id=10, offer_name="Old Offer")
        mock_old_offer = EventOffer(id=10, name="Old Offer", product_ids="2")

        mock_query_product = MagicMock()
        mock_query_product.filter.return_value.all.return_value = [mock_product_2]

        mock_query_offer = MagicMock()
        mock_query_offer.filter.return_value.first.return_value = mock_old_offer

        def db_query_side_effect(model):
            if model == Product:
                return mock_query_product
            if model == EventOffer:
                return mock_query_offer
            return MagicMock()

        self.db_session.query.side_effect = db_query_side_effect

        # Act
        result = self.event_offer_service.update_product_offer(self.db_session, [2], None)

        # Assert
        self.assertEqual(result["updated_count"], 1)
        self.assertEqual(mock_product_2.offer_id, None)
        self.assertEqual(mock_product_2.discounted_price, None)
        self.assertEqual(mock_old_offer.product_ids, "")

if __name__ == '__main__':
    unittest.main()
