from sqlalchemy.orm import Session
from typing import List

from app.models.offer import Offer
from app.models.product import Product
from app.schemas.offer import OfferCreate, OfferUpdate

class OfferService:
    def create_offer(self, db: Session, offer: OfferCreate) -> Offer:
        db_offer = Offer(**offer.dict())
        db.add(db_offer)
        db.commit()
        db.refresh(db_offer)
        return db_offer

    def get_all_offers(self, db: Session) -> List[Offer]:
        return db.query(Offer).all()

    def update_offer(self, db: Session, offer_update: OfferUpdate) -> Offer:
        db_offer = db.query(Offer).filter(Offer.id == offer_update.id).first()
        if db_offer:
            for key, value in offer_update.dict().items():
                setattr(db_offer, key, value)
            db.commit()
            db.refresh(db_offer)
        return db_offer

    def calculate_discounted_price(self, price: int, offer: Offer) -> int:
        if offer.discount_type == "percentage":
            discount = price * (offer.discount_value / 100)
            return price - discount
        elif offer.discount_type == "flat_amount":
            return price - offer.discount_value
        else:
            return price

    def add_products_to_offer(self, db: Session, offer_id: int, product_ids: List[int]) -> Offer:
        db_offer = db.query(Offer).filter(Offer.id == offer_id).first()
        if db_offer:
            for product_id in product_ids:
                product = db.query(Product).filter(Product.id == product_id).first()
                if product:
                    db_offer.products.append(product)
            db.commit()
            db.refresh(db_offer)
        return db_offer
