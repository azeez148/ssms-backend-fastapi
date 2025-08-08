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

    def get_all_event_offers(self, db: Session) -> List[EventOffer]:
        return db.query(EventOffer).all()

    def update_event_offer(self, db: Session, offer_id: int, offer_update: "EventOfferUpdate") -> Optional[EventOffer]:
        db_offer = self.get_event_offer_by_id(db, offer_id)
        if not db_offer:
            return None

        # Store old product/category associations to check for changes
        old_product_ids_str = db_offer.product_ids
        old_category_ids_str = db_offer.category_ids

        # Update the offer fields
        update_data = offer_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "product_ids" or key == "category_ids":
                setattr(db_offer, key, ",".join(map(str, value)))
            else:
                setattr(db_offer, key, value)

        # Check if the offer logic needs to be reapplied
        offer_fields_changed = any(key in update_data for key in ['rate', 'rate_type', 'product_ids', 'category_ids'])

        if offer_fields_changed:
            # Remove the old offer from all associated products
            self.remove_offer_from_products(db, old_product_ids_str, old_category_ids_str)
            # Apply the updated offer
            self.apply_offer_to_products(db, db_offer)

        db.add(db_offer)
        db.commit()
        db.refresh(db_offer)
        return db_offer

    def set_event_offer_active_status(self, db: Session, offer_id: int, is_active: bool) -> Optional[EventOffer]:
        db_offer = self.get_event_offer_by_id(db, offer_id)
        if not db_offer:
            return None

        db_offer.is_active = is_active

        if is_active:
            self.apply_offer_to_products(db, db_offer)
        else:
            self.remove_offer_from_products(db, db_offer.product_ids, db_offer.category_ids)

        db.add(db_offer)
        db.commit()
        db.refresh(db_offer)
        return db_offer

    def remove_offer_from_products(self, db: Session, product_ids_str: str, category_ids_str: str):
        product_service = ProductService()
        product_ids_to_clear = []
        if product_ids_str:
            product_ids_to_clear.extend([int(pid) for pid in product_ids_str.split(',') if pid])

        if category_ids_str:
            category_ids = [int(cid) for cid in category_ids_str.split(',') if cid]
            products_in_categories = db.query(Product).filter(Product.category_id.in_(category_ids)).all()
            for product in products_in_categories:
                product_ids_to_clear.append(product.id)

        for product_id in set(product_ids_to_clear):
            product = product_service.get_product_by_id(db, product_id)
            if product:
                product.offer_id = None
                product.discounted_price = None
                product.offer_price = None
                db.add(product)

        db.commit()

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
