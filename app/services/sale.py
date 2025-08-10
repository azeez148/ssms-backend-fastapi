from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.models.sale import Sale, SaleItem
from app.schemas.customer import CustomerCreate
from app.schemas.sale import SaleCreate
from app.services.customer import get_or_create_customer
from app.services.notification import WhatsAppNotificationService, EmailNotificationService
from app.services.product import ProductService

class SaleService:
    def __init__(self):
        self.whatsapp_notification = WhatsAppNotificationService()
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
            'customer_mobile', 'customer_email'
        })
        sale_data['customer_id'] = customer_id

        db_sale = Sale(**sale_data)
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
                total_price=item.total_price
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
        
        # Send notifications
        self.whatsapp_notification.send_sale_notification(db, db_sale)
        self.email_notification.send_sale_notification(db_sale)
        
        return db_sale

    def get_sale(self, db: Session, sale_id: int) -> Optional[Sale]:
        return db.query(Sale).filter(Sale.id == sale_id).first()

    def get_all_sales(self, db: Session) -> List[Sale]:
        return db.query(Sale).all()

    def get_recent_sales(self, db: Session, limit: int = 10) -> List[Sale]:
        return db.query(Sale).order_by(Sale.date.desc()).limit(limit).all()

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
