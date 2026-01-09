from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict
from app.models.sale import Sale, SaleItem
from app.schemas.customer import CustomerCreate
from app.schemas.sale import SaleCreate
from app.schemas.enums import SaleStatus
from app.services.customer import get_or_create_customer
from app.services.notification import EmailNotificationService
from app.services.product import ProductService

class SaleService:
    def __init__(self):
        self.email_notification = EmailNotificationService()
        self.product_service = ProductService()

    def create_sale(self, db: Session, sale: SaleCreate) -> Sale:
        # Get or create customer
        customer_id = sale.customer_id
        if customer_id == 0:
            if not sale.customer_mobile:
                raise ValueError("Customer mobile number is required to create a new customer.")

            customer_data = CustomerCreate(
                name=sale.customer_name,
                address=sale.customer_address,
                mobile=sale.customer_mobile,
                email=sale.customer_email
            )
            customer = get_or_create_customer(db, customer_data)
            customer_id = customer.id

        # Create the main sale record
        sale_data = sale.model_dump(exclude={
            'sale_items', 'customer_name', 'customer_address',
            'customer_mobile', 'customer_email', 'status'
        })
        sale_data['customer_id'] = customer_id

        # Set status: use provided status if available, else default to COMPLETED
        status = getattr(sale, "status", SaleStatus.COMPLETED) or SaleStatus.COMPLETED

        db_sale = Sale(**sale_data, created_by="system", updated_by="system", status=status)
        db.add(db_sale)
        db.flush()  # Get the sale ID without committing

        # Create sale items and update stock
        for item in sale.sale_items:
            sale_item = SaleItem(
                sale_id=db_sale.id,
                product_id=item.product_id,
                product_name=item.product_name,
                product_category=item.product_category,
                size=item.size,
                quantity_available=item.quantity_available,
                quantity=item.quantity,
                sale_price=item.sale_price,
                total_price=item.total_price,
                created_by="system",
                updated_by="system"
            )
            db.add(sale_item)
            
            # Update product stock
            self.product_service.update_product_stock(
                db,
                product_id=item.product_id,
                size=item.size,
                
                quantity_change=-item.quantity  # Decrease stock by sold quantity
            )

        db.commit()
        db.refresh(db_sale)
        
        try:
            # Send notifications
            self.email_notification.send_sale_notification(db_sale)
        except Exception as e:
            print(str(e))
            pass
        
        return db_sale

    def get_sale(self, db: Session, sale_id: int) -> Optional[Sale]:
        return db.query(Sale).filter(Sale.id == sale_id).first()

    def get_all_sales(self, db: Session) -> List[Sale]:
        return db.query(Sale).options(joinedload(Sale.customer)).all()

    def get_recent_sales(self, db: Session, limit: int = 10) -> List[Sale]:
        return db.query(Sale).options(joinedload(Sale.customer)).order_by(Sale.date.desc()).limit(limit).all()

    def get_most_sold_items(self, db: Session) -> Dict[int, Dict]:
        """Get a summary of most sold items with product details"""
        sales_items = db.query(SaleItem).all()
        item_stats = {}
        
        for item in sales_items:
            if item.product_id not in item_stats:
                item_stats[item.product_id] = {
                    'product_name': item.product_name,
                    'product_category': item.product_category,
                    'total_quantity': 0,
                    'total_revenue': 0.0
                }
            
            stats = item_stats[item.product_id]
            stats['total_quantity'] += item.quantity
            stats['total_revenue'] += item.total_price
        
        return item_stats

    def get_total_sales(self, db: Session) -> dict:
        """Get total sales summary"""
        sales = db.query(Sale).all()
        return {
            'total_count': len(sales),
            'total_revenue': sum(sale.total_price for sale in sales),
            'total_items_sold': sum(sale.total_quantity for sale in sales)
        }

    def update_sale_status(self, db: Session, sale_id: int, status: str) -> Optional[Sale]:
        sale = self.get_sale(db, sale_id)
        if sale:
            sale.status = SaleStatus(status)
            db.commit()
            db.refresh(sale)
        return sale

    # implement cancel_sale
    def cancel_sale(self, db: Session, sale_id: int) -> Optional[Sale]:
        sale = self.get_sale(db, sale_id)
        if sale and sale.status != SaleStatus.CANCELLED:
            sale.status = SaleStatus.CANCELLED
            
            # Restore product stock
            for item in sale.sale_items:
                self.product_service.update_product_stock(
                    db,
                    product_id=item.product_id,
                    size=item.size,
                    quantity_change=item.quantity  # Increase stock by cancelled quantity
                )
            
            db.commit()
            db.refresh(sale)
        return sale

    def update_sale(self, db: Session, sale_data: SaleCreate, sale_id: int) -> Optional[Sale]:
        sale = self.get_sale(db, sale_id)
        if not sale:
            return None

        # Update main sale fields
        for field, value in sale_data.model_dump(exclude={'sale_items'}).items():
            setattr(sale, field, value)

        # Clear existing sale items
        db.query(SaleItem).filter(SaleItem.sale_id == sale.id).delete()

        # Add updated sale items and adjust stock
        for item in sale_data.sale_items:
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=item.product_id,
                product_name=item.product_name,
                product_category=item.product_category,
                size=item.size,
                quantity_available=item.quantity_available,
                quantity=item.quantity,
                sale_price=item.sale_price,
                total_price=item.total_price,
                created_by="system",
                updated_by="system"
            )
            db.add(sale_item)

        db.commit()
        db.refresh(sale)
        return sale