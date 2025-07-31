from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class OfferBase(BaseModel):
    name: str
    discount_type: str
    discount_value: int
    start_date: date
    end_date: date
    is_active: bool

class OfferCreate(OfferBase):
    pass

class OfferUpdate(OfferBase):
    pass

class OfferResponse(OfferBase):
    id: int
    products: List["ProductResponse"] = []

    class Config:
        orm_mode = True

from app.schemas.product import ProductResponse
OfferResponse.update_forward_refs()
