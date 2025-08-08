from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class EventOfferBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: str
    is_active: bool
    start_date: datetime
    end_date: datetime
    rate_type: str
    rate: int
    product_ids: List[int] = []
    category_ids: List[int] = []

    class Config:
        from_attributes = True

class EventOfferCreate(EventOfferBase):
    pass

class EventOfferInDB(EventOfferBase):
    id: int

class EventOfferResponse(EventOfferInDB):
    pass
