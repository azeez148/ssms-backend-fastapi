from sqlalchemy.orm import Session
from typing import Dict
from app.services.sale import SaleService
from app.services.product import ProductService
from app.services.category import CategoryService
from app.services.purchase import PurchaseService

class DashboardService:
    def __init__(self):
        self.sale_service = SaleService()
        self.product_service = ProductService()
        self.category_service = CategoryService()
        self.purchase_service = PurchaseService()

    def get_dashboard_data(self, db: Session) -> Dict:
        return {
            "total_sales": self.sale_service.get_total_sales(db),
            "total_products": len(self.product_service.get_all_products(db)),
            "total_categories": len(self.category_service.get_all_categories(db)),
            "most_sold_items": self.sale_service.get_most_sold_items(db),
            "recent_sales": self.sale_service.get_recent_sales(db),
            "total_purchases": self.purchase_service.get_total_purchases(db),
            "recent_purchases": self.purchase_service.get_recent_purchases(db)
        }
