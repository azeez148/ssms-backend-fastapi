from pydantic import BaseModel
from typing import List, Optional


class StockSummary(BaseModel):
    product_count: int
    total_units: int
    total_value: float


class SoldItemInsight(BaseModel):
    product_id: Optional[int] = None
    product_name: str
    total_quantity: int
    total_revenue: float
    total_profit_loss: float


class DashboardContext(BaseModel):
    period: str
    start_date: str
    end_date: str
    shop_id: Optional[int] = None
    shop_name: str


class DashboardMetrics(BaseModel):
    in_stock_summary: StockSummary
    out_of_stock_summary: StockSummary
    most_sold_items: List[SoldItemInsight]
    least_sold_items: List[SoldItemInsight]
    total_in_stock_value: float
    expected_sales_value: float
    expected_profit_loss: float
    current_sales: float
    current_profit_loss: float


class DashboardV2Response(BaseModel):
    context: DashboardContext
    metrics: DashboardMetrics
