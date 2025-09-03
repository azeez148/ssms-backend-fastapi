from pydantic import BaseModel
from typing import List, Optional

class StockItem(BaseModel):
    product_id: int
    size: str
    quantity: int

class StockRequest(BaseModel):
    items: List[StockItem]

class StockResponse(BaseModel):
    success: bool
    message: Optional[str] = None
