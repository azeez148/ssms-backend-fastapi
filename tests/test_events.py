import unittest
from unittest.mock import MagicMock, patch
from app.services.event import EventOfferService
from app.schemas.event import EventOfferCreate
from app.models.product import Product
from app.models.event import EventOffer
from datetime import datetime

class TestEvents(unittest.TestCase):

    @patch('app.services.event.ProductService')
    def test_create_event_offer(self, MockProductService):
        # Arrange
        db_session = MagicMock()
        mock_product_service = MockProductService.return_value

        event_offer_create = EventOfferCreate(
            name="Test Offer",
            description="Test Description",
            type="offer",
            is_active=True,
            start_date=datetime.now(),
            end_date=datetime.now(),
            rate_type="flat",
            rate=10,
            product_ids=[1, 2],
            category_ids=[3]
        )

        # Mock products
        mock_product_1 = Product(id=1, name="Product 1", selling_price=100, category_id=1)
        mock_product_2 = Product(id=2, name="Product 2", selling_price=200, category_id=2)
        mock_product_3 = Product(id=3, name="Product 3", selling_price=300, category_id=3)

        def get_product_by_id(db, product_id):
            if product_id == 1:
                return mock_product_1
            if product_id == 2:
                return mock_product_2
            if product_id == 3:
                return mock_product_3
            return None

        mock_product_service.get_product_by_id.side_effect = get_product_by_id

        db_session.query(Product).filter.return_value.all.return_value = [mock_product_3]


        event_offer_service = EventOfferService()

        # Act
        created_event_offer = event_offer_service.create_event_offer(db_session, event_offer_create)

        # Assert
        self.assertEqual(created_event_offer.name, "Test Offer")
        self.assertEqual(mock_product_1.discounted_price, 90)
        self.assertEqual(mock_product_2.discounted_price, 190)
        self.assertEqual(mock_product_3.discounted_price, 290)

if __name__ == '__main__':
    unittest.main()
