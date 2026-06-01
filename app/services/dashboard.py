from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Dict
from app.models.category import Category
from app.models.product import Product
from app.services.sale import SaleService
from app.services.purchase import PurchaseService

class DashboardService:
    def __init__(self):
        self.sale_service = SaleService()
        self.purchase_service = PurchaseService()

    def get_dashboard_data(self, db: Session) -> Dict:
        total_products = db.query(func.count(Product.id)).scalar() or 0
        total_categories = db.query(func.count(Category.id)).scalar() or 0

        return {
            "total_sales": self.sale_service.get_total_sales(db),
            "total_products": int(total_products),
            "total_categories": int(total_categories),
            "most_sold_items": self.sale_service.get_most_sold_items(db),
            "recent_sales": self.sale_service.get_recent_sales(db),
            "total_purchases": self.purchase_service.get_total_purchases(db),
            "recent_purchases": self.purchase_service.get_recent_purchases(db)
        }
