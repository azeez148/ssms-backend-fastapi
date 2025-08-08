from sqlalchemy.orm import Session
from app.models.event import EventOffer, RateType
from app.models.product import Product
from app.schemas.event import EventOfferCreate
from typing import Optional, List
from app.services.product import ProductService

class EventOfferService:
    def create_event_offer(self, db: Session, event_offer: EventOfferCreate) -> EventOffer:
        db_event_offer = EventOffer(
            name=event_offer.name,
            description=event_offer.description,
            type=event_offer.type,
            is_active=event_offer.is_active,
            start_date=event_offer.start_date,
            end_date=event_offer.end_date,
            rate_type=event_offer.rate_type,
            rate=event_offer.rate,
            product_ids=",".join(map(str, event_offer.product_ids)),
            category_ids=",".join(map(str, event_offer.category_ids)),
        )
        db.add(db_event_offer)
        db.commit()
        db.refresh(db_event_offer)

        self.apply_offer_to_products(db, db_event_offer)

        return db_event_offer

    def get_event_offer_by_id(self, db: Session, offer_id: int) -> Optional[EventOffer]:
        return db.query(EventOffer).filter(EventOffer.id == offer_id).first()

    def apply_offer_to_products(self, db: Session, offer: EventOffer):
        product_service = ProductService()
        product_ids_to_update = []
        if offer.product_ids:
            product_ids_to_update.extend([int(pid) for pid in offer.product_ids.split(',')])

        if offer.category_ids:
            category_ids = [int(cid) for cid in offer.category_ids.split(',')]
            products_in_categories = db.query(Product).filter(Product.category_id.in_(category_ids)).all()
            for product in products_in_categories:
                product_ids_to_update.append(product.id)

        for product_id in set(product_ids_to_update):
            product = product_service.get_product_by_id(db, product_id)
            if product:
                if offer.rate_type == RateType.flat:
                    product.discounted_price = product.selling_price - offer.rate
                    product.offer_price = offer.rate
                elif offer.rate_type == RateType.percentage:
                    product.offer_price = (product.selling_price * offer.rate) / 100
                    product.discounted_price = product.selling_price - product.offer_price

                product.offer_id = offer.id
                db.add(product)
        db.commit()
