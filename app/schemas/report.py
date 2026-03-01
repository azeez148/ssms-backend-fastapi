from pydantic import BaseModel
from typing import List, Dict, Optional
from app.schemas.sale import SaleResponse

class SaleItemDetail(BaseModel):
    product_name: str
    size: str
    quantity: int
    unit_price: float
    sale_price: float
    profit_loss: float

class SalesReportResponse(BaseModel):
    sales: List[SaleResponse]
    total_sales: int
    status_breakdown: Dict[str, int]
    total_quantity: int
    total_revenue: float
    total_profit: float
    sale_item_details: List[SaleItemDetail] = []

class SalesReportSummary(BaseModel):
    period_label: str
    start_date: str
    end_date: str
    total_sales: int
    total_quantity: int
    total_revenue: float
    total_profit: float
    status_breakdown: Dict[str, int]

class SalesComparisonDifference(BaseModel):
    total_sales: int
    total_quantity: int
    total_revenue: float
    total_profit: float
    total_sales_pct_change: Optional[float] = None
    total_revenue_pct_change: Optional[float] = None
    total_profit_pct_change: Optional[float] = None

class SalesComparisonResponse(BaseModel):
    period_1: SalesReportSummary
    period_2: SalesReportSummary
    difference: SalesComparisonDifference
