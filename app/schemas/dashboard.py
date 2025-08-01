from pydantic import BaseModel
from typing import Dict, List
from app.schemas.sale import SaleResponse
from app.schemas.purchase import PurchaseResponse

class Dashboard(BaseModel):
    total_sales: Dict
    total_products: int
    total_categories: int
    most_sold_items: Dict
    recent_sales: List[SaleResponse]
    total_purchases: Dict
    recent_purchases: List[PurchaseResponse]
    
    class Config:
        from_attributes = True
