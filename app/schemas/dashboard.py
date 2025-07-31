from pydantic import BaseModel
from typing import Dict, List
from app.schemas.sale import SaleResponse

class Dashboard(BaseModel):
    total_sales: Dict
    total_products: int
    total_categories: int
    most_sold_items: Dict
    recent_sales: List[SaleResponse]
    
    class Config:
        from_attributes = True
