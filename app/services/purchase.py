from sqlalchemy.orm import Session
from typing import List
from app.models.purchase import Purchase, PurchaseItem
from app.models.product import Product
from app.models.product_size import ProductSize
from app.models.shop import Shop
from app.schemas.purchase import PurchaseCreate

class PurchaseService:
    def create_purchase(self, db: Session, purchase: PurchaseCreate) -> Purchase:
        # Create PurchaseItem models from the purchase data
        purchase_items = [PurchaseItem(**item.dict()) for item in purchase.purchase_items]

        # Create the main Purchase object
        db_purchase = Purchase(
            supplier_name=purchase.supplier_name,
            supplier_address=purchase.supplier_address,
            supplier_mobile=purchase.supplier_mobile,
            supplier_email=purchase.supplier_email,
            date=purchase.date,
            total_quantity=purchase.total_quantity,
            total_price=purchase.total_price,
            payment_type_id=purchase.payment_type_id,
            payment_reference_number=purchase.payment_reference_number,
            delivery_type_id=purchase.delivery_type_id,
            purchase_items=purchase_items
        )

        # Add shops to the purchase
        if purchase.shop_ids:
            shops = db.query(Shop).filter(Shop.id.in_(purchase.shop_ids)).all()
            db_purchase.shops.extend(shops)

        # Update product quantities
        for item in purchase.purchase_items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                # Find the size in the product's size_map
                product_size = None
                for size in product.size_map:
                    if size.size == item.size:
                        product_size = size
                        break

                if product_size:
                    product_size.quantity += item.quantity
                else:
                    # If the size doesn't exist, create a new one
                    new_product_size = ProductSize(
                        product_id=product.id,
                        size=item.size,
                        quantity=item.quantity
                    )
                    db.add(new_product_size)

        db.add(db_purchase)
        db.commit()
        db.refresh(db_purchase)
        return db_purchase

    def get_all_purchases(self, db: Session) -> List[Purchase]:
        return db.query(Purchase).all()

    def get_purchase_by_id(self, db: Session, purchase_id: int) -> Purchase:
        return db.query(Purchase).filter(Purchase.id == purchase_id).first()
