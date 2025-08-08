import unittest
from unittest.mock import MagicMock, patch
from app.services.event import EventOfferService
from app.schemas.event import EventOfferCreate
from app.models.product import Product
from app.models.event import EventOffer, RateType
from app.schemas.event import EventOfferUpdate
from datetime import datetime

class TestEvents(unittest.TestCase):

    def setUp(self):
        self.event_offer_service = EventOfferService()
        self.db_session = MagicMock()

        # Mock products
        self.mock_product_1 = Product(id=1, name="Product 1", selling_price=100, category_id=1)
        self.mock_product_2 = Product(id=2, name="Product 2", selling_price=200, category_id=2)
        self.mock_product_3 = Product(id=3, name="Product 3", selling_price=300, category_id=3)

    def mock_get_product_by_id(self, db, product_id):
        if product_id == 1:
            return self.mock_product_1
        if product_id == 2:
            return self.mock_product_2
        if product_id == 3:
            return self.mock_product_3
        return None

    @patch('app.services.event.ProductService')
    def test_create_event_offer(self, MockProductService):
        # Arrange
        mock_product_service = MockProductService.return_value
        mock_product_service.get_product_by_id.side_effect = self.mock_get_product_by_id
        self.db_session.query(Product).filter.return_value.all.return_value = [self.mock_product_3]

        def mock_refresh(obj):
            if isinstance(obj, EventOffer):
                obj.rate_type = RateType(obj.rate_type)

        self.db_session.refresh.side_effect = mock_refresh

        event_offer_create = EventOfferCreate(
            name="Test Offer", description="Test Description", type="offer",
            is_active=True, start_date=datetime.now(), end_date=datetime.now(),
            rate_type="flat", rate=10, product_ids=[1, 2], category_ids=[3]
        )

        # Act
        created_event_offer = self.event_offer_service.create_event_offer(self.db_session, event_offer_create)

        # Assert
        self.assertEqual(created_event_offer.name, "Test Offer")
        self.assertEqual(self.mock_product_1.discounted_price, 90)
        self.assertEqual(self.mock_product_2.discounted_price, 190)
        self.assertEqual(self.mock_product_3.discounted_price, 290)

    def test_get_all_event_offers(self):
        # Arrange
        mock_offer = EventOffer(id=1, name="Test Offer")
        self.db_session.query(EventOffer).all.return_value = [mock_offer]

        # Act
        offers = self.event_offer_service.get_all_event_offers(self.db_session)

        # Assert
        self.assertEqual(len(offers), 1)
        self.assertEqual(offers[0].name, "Test Offer")

    @patch('app.services.event.ProductService')
    def test_update_event_offer(self, MockProductService):
        # Arrange
        mock_product_service = MockProductService.return_value
        mock_product_service.get_product_by_id.side_effect = self.mock_get_product_by_id
        self.db_session.query(Product).filter.return_value.all.return_value = []

        mock_offer = EventOffer(
            id=1, name="Old Offer", rate_type=RateType.flat, rate=10,
            product_ids="1", category_ids=""
        )
        self.db_session.query(EventOffer).filter.return_value.first.return_value = mock_offer

        offer_update = EventOfferUpdate(rate=20, product_ids=[2])

        # Act
        self.event_offer_service.update_event_offer(self.db_session, 1, offer_update)

        # Assert
        self.assertEqual(self.mock_product_1.offer_id, None)
        self.assertEqual(self.mock_product_2.discounted_price, 180) # 200 - 20

    @patch('app.services.event.ProductService')
    def test_set_active_status_deactivate(self, MockProductService):
        # Arrange
        mock_product_service = MockProductService.return_value
        mock_product_service.get_product_by_id.side_effect = self.mock_get_product_by_id

        mock_offer = EventOffer(
            id=1, name="Active Offer", is_active=True,
            product_ids="1", category_ids=""
        )
        self.db_session.query(EventOffer).filter.return_value.first.return_value = mock_offer

        # Act
        self.event_offer_service.set_event_offer_active_status(self.db_session, 1, is_active=False)

        # Assert
        self.assertEqual(mock_offer.is_active, False)
        self.assertEqual(self.mock_product_1.offer_id, None)

    @patch('app.services.event.ProductService')
    def test_set_active_status_activate(self, MockProductService):
        # Arrange
        mock_product_service = MockProductService.return_value
        mock_product_service.get_product_by_id.side_effect = self.mock_get_product_by_id

        mock_offer = EventOffer(
            id=1, name="Inactive Offer", is_active=False,
            rate_type=RateType.flat, rate=10,
            product_ids="1", category_ids=""
        )
        self.db_session.query(EventOffer).filter.return_value.first.return_value = mock_offer

        # Act
        self.event_offer_service.set_event_offer_active_status(self.db_session, 1, is_active=True)

        # Assert
        self.assertEqual(mock_offer.is_active, True)
        self.assertEqual(self.mock_product_1.discounted_price, 90)


if __name__ == '__main__':
    unittest.main()
