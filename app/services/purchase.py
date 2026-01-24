from sqlalchemy.orm import Session
from typing import List
from app.models.purchase import Purchase, PurchaseItem
from app.models.user import User
from app.schemas.enums import UserRole
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
            shop_id=purchase.shop_id,
            created_by="system",
            updated_by="system"
        )

        # Update product quantities for specific shop
        for item in purchase.purchase_items:
            product_size = db.query(ProductSize).filter(
                ProductSize.product_id == item.product_id,
                ProductSize.size == item.size,
                ProductSize.shop_id == purchase.shop_id
            ).first()

            if product_size:
                product_size.quantity += item.quantity
            else:
                # If the size doesn't exist for this shop, create a new one
                new_product_size = ProductSize(
                    product_id=item.product_id,
                    shop_id=purchase.shop_id,
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

    def get_all_purchases(self, db: Session, user: Optional[User] = None) -> List[Purchase]:
        query = db.query(Purchase)
        if user and user.role != UserRole.ADMINISTRATOR:
            shop_ids = [shop.id for shop in user.shops]
            query = query.filter(Purchase.shop_id.in_(shop_ids))
        return query.all()

    def get_purchase_by_id(self, db: Session, purchase_id: int, user: Optional[User] = None) -> Purchase:
        query = db.query(Purchase).filter(Purchase.id == purchase_id)
        if user and user.role != UserRole.ADMINISTRATOR:
            shop_ids = [shop.id for shop in user.shops]
            query = query.filter(Purchase.shop_id.in_(shop_ids))
        return query.first()

    def get_recent_purchases(self, db: Session, user: Optional[User] = None, limit: int = 10) -> List[Purchase]:
        query = db.query(Purchase)
        if user and user.role != UserRole.ADMINISTRATOR:
            shop_ids = [shop.id for shop in user.shops]
            query = query.filter(Purchase.shop_id.in_(shop_ids))
        return query.order_by(Purchase.date.desc()).limit(limit).all()

    def get_total_purchases(self, db: Session) -> dict:
        """Get total purchases summary"""
        purchases = self.get_all_purchases(db)
        return {
            'total_count': len(purchases),
            'total_cost': sum(purchase.total_price for purchase in purchases),
            'total_items_purchased': sum(purchase.total_quantity for purchase in purchases)
        }
