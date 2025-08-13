from sqlalchemy.orm import Session
from app.schemas.home import HomeResponse
from app.services.product import ProductService
from app.services.event import EventOfferService
from app.models.event import EventOffer
from typing import List

class HomeService:
    def __init__(self):
        self.product_service = ProductService()
        self.event_offer_service = EventOfferService()

    def get_home_data(self, db: Session) -> HomeResponse:
        products = self.product_service.get_all_products(db)
        return HomeResponse(products=products)

    def get_active_offers(self, db: Session) -> List[EventOffer]:
        return self.event_offer_service.get_active_event_offers(db)
