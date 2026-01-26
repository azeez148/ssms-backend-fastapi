from sqlalchemy.orm import Session
from app.models.event import EventOffer, RateType
from app.models.product import Product
from typing import List, Optional

class OfferService:
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

                # Use rate and rate_type to calculate prices
                # Assuming selling_price is an integer
                if new_offer.rate_type == RateType.flat:
                    product.offer_price = new_offer.rate
                    product.discounted_price = (product.selling_price or 0) - (new_offer.rate or 0)
                elif new_offer.rate_type == RateType.percentage:
                    product.offer_price = ((product.selling_price or 0) * (new_offer.rate or 0)) / 100
                    product.discounted_price = (product.selling_price or 0) - (product.offer_price or 0)
                else:
                    # Fallback if rate_type is something else
                    product.offer_price = 0
                    product.discounted_price = product.selling_price
            else:
                product.offer_id = None
                product.offer_name = None
                product.offer_price = None
                product.discounted_price = None

        # Update product_ids strings in EventOffers to maintain consistency
        # 1. Remove these product IDs from their old offers
        for old_id in old_offer_ids:
            if new_offer and old_id == new_offer.id:
                continue
            off = db.query(EventOffer).filter(EventOffer.id == old_id).first()
            if off and off.product_ids:
                pids = [pid for pid in off.product_ids.split(',') if pid and int(pid) not in actual_product_ids]
                off.product_ids = ",".join(pids)

        # 2. Add these product IDs to the new offer
        if new_offer:
            current_pids = [pid for pid in (new_offer.product_ids.split(',') if new_offer.product_ids else []) if pid]
            current_pids_set = set(current_pids)
            for pid in actual_product_ids:
                if str(pid) not in current_pids_set:
                    current_pids.append(str(pid))
            new_offer.product_ids = ",".join(current_pids)

        db.commit()
        return {"message": "Offer updated successfully", "updated_count": len(actual_product_ids)}
