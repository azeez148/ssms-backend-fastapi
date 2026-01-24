from pydantic import BaseModel, Field
from typing import List, Optional

class StockItem(BaseModel):
    product_id: int = Field(..., alias='productId')
    size: str
    quantity: int

class StockRequest(BaseModel):
    items: List[StockItem]
    shop_id: Optional[int] = None

class StockResponse(BaseModel):
    success: bool
    message: Optional[str] = None
