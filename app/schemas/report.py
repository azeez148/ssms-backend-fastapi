from pydantic import BaseModel
from typing import List, Dict, Optional
from app.schemas.sale import SaleResponse

class SalesReportResponse(BaseModel):
    sales: List[SaleResponse]
    total_sales: int
    status_breakdown: Dict[str, int]
    total_amount: float
    total_quantity: int
