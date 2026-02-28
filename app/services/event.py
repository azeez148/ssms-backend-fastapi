from sqlalchemy.orm import Session
from app.models.category_discount import CategoryDiscount
from app.models.event import EventOffer, RateType
from app.models.product import Product
from app.schemas.event import EventOfferCreate
from typing import Optional, List
from app.services.product import ProductService
from datetime import datetime

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
            created_by="system",
            updated_by="system",
            code=event_offer.code
        )
        db.add(db_event_offer)
        db.commit()
        db.refresh(db_event_offer)

        self.apply_offer_to_products(db, db_event_offer)

        return db_event_offer

    def get_event_offer_by_id(self, db: Session, offer_id: int) -> Optional[EventOffer]:
        return db.query(EventOffer).filter(EventOffer.id == offer_id).first()

    def get_event_offer_by_code(self, db: Session, code: str) -> Optional[EventOffer]:
        return db.query(EventOffer).filter(EventOffer.code == code).first()

    def get_all_event_offers(self, db: Session) -> List[EventOffer]:
        return db.query(EventOffer).all()

    def get_active_event_offers(self, db: Session) -> List[EventOffer]:
        now = datetime.now()
        return db.query(EventOffer).filter(
            EventOffer.is_active == True,
            EventOffer.start_date <= now,
            EventOffer.end_date >= now
        ).all()

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

        db_offer.updated_by = "system"
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

        db_offer.updated_by = "system"
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
                product.discounted_price = self.find_original_discounted_price(db, product)
                product.offer_price = None
                product.offer_name = None
                db.add(product)

        db.commit()
    
    def find_original_discounted_price(self, db: Session, product: Product) -> Optional[int]:
        """Calculate the original discounted price based on category discount and product attributes."""
        default_discount = self.get_default_category_discount(db, product.category_id)
        
        if not default_discount or default_discount.discounted_price is None:
            return product.selling_price - 50
        
        discounted_price = default_discount.discounted_price
        
        # Apply additional adjustments based on product name
        if product.name:
            has_embroidery = "embroidery" in product.name.lower()
            has_collar = "collar" in product.name.lower()
            
            if has_embroidery and has_collar:
                discounted_price += 75
            elif has_embroidery or has_collar:
                discounted_price += 50
        
        return discounted_price

    
    def get_default_category_discount(self, db: Session, category_id: int) -> Optional[CategoryDiscount]:
        # Placeholder implementation, replace with actual database query to fetch default category discount
        return db.query(CategoryDiscount).filter(CategoryDiscount.category_id == category_id).first()

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
                    product.offer_name = offer.name
                elif offer.rate_type == RateType.percentage:
                    product.offer_price = (product.selling_price * offer.rate) / 100
                    product.discounted_price = product.selling_price - product.offer_price
                    product.offer_name = offer.name

                product.offer_id = offer.id
                db.add(product)
        db.commit()

    def update_product_offer(self, db: Session, product_ids: List[int], offer_id: Optional[int]):
        # Fetch products that exist in the database
        products = db.query(Product).filter(Product.id.in_(product_ids)).all()
        actual_product_ids = [p.id for p in products]

        if not products:
            return {"message": "No valid products found to update", "updated_count": 0}

        # Get all unique old offer IDs from these products
        old_offer_ids = {p.offer_id for p in products if p.offer_id}

        new_offer = None
        if offer_id is not None:
            new_offer = db.query(EventOffer).filter(EventOffer.id == offer_id).first()
            if not new_offer:
                raise ValueError(f"Offer with id {offer_id} not found")

        # Update products
        for product in products:
            if new_offer:
                product.offer_id = new_offer.id
                product.offer_name = new_offer.name

                if new_offer.rate_type == RateType.flat:
                    product.offer_price = new_offer.rate
                    product.discounted_price = (product.selling_price or 0) - (new_offer.rate or 0)
                elif new_offer.rate_type == RateType.percentage:
                    product.offer_price = ((product.selling_price or 0) * (new_offer.rate or 0)) / 100
                    product.discounted_price = (product.selling_price or 0) - (product.offer_price or 0)
                else:
                    product.offer_price = 0
                    product.discounted_price = product.selling_price
            else:
                product.offer_id = None
                product.offer_name = None
                product.offer_price = None
                product.discounted_price = self.find_original_discounted_price(db, product)
            db.add(product)

        # Update product_ids strings in EventOffers to maintain consistency
        for old_id in old_offer_ids:
            if new_offer and old_id == new_offer.id:
                continue
            off = db.query(EventOffer).filter(EventOffer.id == old_id).first()
            if off and off.product_ids:
                pids = [pid for pid in off.product_ids.split(',') if pid and int(pid) not in actual_product_ids]
                off.product_ids = ",".join(pids)
                db.add(off)

        if new_offer:
            current_pids = [pid for pid in (new_offer.product_ids.split(',') if new_offer.product_ids else []) if pid]
            current_pids_set = set(current_pids)
            for pid in actual_product_ids:
                if str(pid) not in current_pids_set:
                    current_pids.append(str(pid))
            new_offer.product_ids = ",".join(current_pids)
            db.add(new_offer)

        db.commit()
        return {"message": "Offer updated successfully", "updated_count": len(actual_product_ids)}
