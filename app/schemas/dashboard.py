from pydantic import BaseModel
from typing import Dict

class Dashboard(BaseModel):
    total_sales: int
    total_products: int
    total_categories: int
    most_sold_items: Dict[str, int]
    recent_sales: list
    
    class Config:
        orm_mode = True
