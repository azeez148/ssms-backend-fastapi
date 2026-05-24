from pydantic import BaseModel
from typing import List, Optional, Dict
from app.schemas.base import BaseSchema

class PerformanceMetrics(BaseModel):
    revenue: float = 0.0
    profit: float = 0.0
    orders: int = 0
    items_sold: int = 0

class DashboardV2Performance(BaseModel):
    daily: PerformanceMetrics
    weekly: PerformanceMetrics
    monthly: PerformanceMetrics
    yearly: PerformanceMetrics
    custom: Optional[PerformanceMetrics] = None

class StockInsightItem(BaseModel):
    product_id: int
    product_name: str
    quantity_sold: int = 0
    current_stock: int = 0

class DashboardV2StockInsights(BaseModel):
    total_instock_items: int = 0
    out_of_stock_items: int = 0
    most_sold: List[StockInsightItem] = []
    less_sold: List[StockInsightItem] = []

class DashboardV2Financials(BaseModel):
    total_instock_value: float = 0.0
    expected_sales_value: float = 0.0
    expected_profit_loss: float = 0.0
    current_sales: float = 0.0
    current_profit_loss: float = 0.0

class DashboardV2Response(BaseSchema):
    performance: DashboardV2Performance
    stock_insights: DashboardV2StockInsights
    financials: DashboardV2Financials

    class Config:
        from_attributes = True
