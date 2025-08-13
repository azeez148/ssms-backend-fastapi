from sqlalchemy.orm import Session
from typing import List
from app.models.purchase import Purchase, PurchaseItem
from app.models.product import Product
from app.models.product_size import ProductSize
from app.models.shop import Shop
from app.schemas.purchase import PurchaseCreate
from app.schemas.vendor import VendorCreate
from app.services.notification import EmailNotificationService
from app.services.vendor import create_vendor

class PurchaseService:
    def create_purchase(self, db: Session, purchase: PurchaseCreate) -> Purchase:
        vendor_id = purchase.vendor_id
        if vendor_id == 0:
            vendor_data = VendorCreate(
                name=purchase.supplier_name,
                address=purchase.supplier_address,
                mobile=purchase.supplier_mobile,
                email=purchase.supplier_email
            )
            new_vendor = create_vendor(db, vendor_data)
            vendor_id = new_vendor.id

        # Create PurchaseItem models from the purchase data
        purchase_items = [PurchaseItem(**item.dict()) for item in purchase.purchase_items]

        # Create the main Purchase object
        db_purchase = Purchase(
            date=purchase.date,
            total_quantity=purchase.total_quantity,
            total_price=purchase.total_price,
            payment_type_id=purchase.payment_type_id,
            payment_reference_number=purchase.payment_reference_number,
            delivery_type_id=purchase.delivery_type_id,
            vendor_id=vendor_id,
            purchase_items=purchase_items,
            created_by="system",
            updated_by="system"
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

        # Send email notification
        notification_service = EmailNotificationService()
        notification_service.send_purchase_notification(db_purchase)

        return db_purchase

    def get_all_purchases(self, db: Session) -> List[Purchase]:
        return db.query(Purchase).all()

    def get_purchase_by_id(self, db: Session, purchase_id: int) -> Purchase:
        return db.query(Purchase).filter(Purchase.id == purchase_id).first()

    def get_recent_purchases(self, db: Session, limit: int = 10) -> List[Purchase]:
        return db.query(Purchase).order_by(Purchase.date.desc()).limit(limit).all()

    def get_total_purchases(self, db: Session) -> dict:
        """Get total purchases summary"""
        purchases = self.get_all_purchases(db)
        return {
            'total_count': len(purchases),
            'total_cost': sum(purchase.total_price for purchase in purchases),
            'total_items_purchased': sum(purchase.total_quantity for purchase in purchases)
        }
