from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PurchaseBase(BaseModel):
    quantity: int
    unit_price: float
    total_price: float
    product_id: int
    shop_id: int

    class Config:
        from_attributes = True

class PurchaseCreate(PurchaseBase):
    pass

class PurchaseInDB(PurchaseBase):
    id: int
    purchase_date: datetime

class PurchaseResponse(PurchaseInDB):
    pass
