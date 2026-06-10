from pydantic import BaseModel, ConfigDict
from typing import Dict, List
from app.schemas.sale import SaleResponse
from app.schemas.purchase import PurchaseResponse
from app.schemas.base import BaseSchema

class SalesSummary(BaseModel):
    total_count: int
    total_revenue: float
    total_items_sold: int

class PurchasesSummary(BaseModel):
    total_count: int
    total_cost: float
    total_items_purchased: int

class InventorySummary(BaseModel):
    total_stock_value: float
    projected_sale_value: float
    projected_profit_value: float

class MostSoldItem(BaseModel):
    product_name: str
    product_category: str
    total_quantity: int
    total_revenue: float

class Dashboard(BaseSchema):
    total_sales: SalesSummary
    todays_sales: SalesSummary
    pending_sales: SalesSummary
    shipped_sales: SalesSummary
    total_purchases: PurchasesSummary
    todays_purchases: PurchasesSummary
    total_products: int
    total_categories: int
    inventory_summary: InventorySummary
    most_sold_items: Dict[str, MostSoldItem]
    recent_sales: List[SaleResponse]
    recent_purchases: List[PurchaseResponse]
    
    model_config = ConfigDict(from_attributes=True)
