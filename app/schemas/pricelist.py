from pydantic import BaseModel
from typing import Optional
from app.schemas.base import BaseSchema

class PricelistBase(BaseModel):
    category_id: int
    unit_price: int = 0
    selling_price: int = 0
    discounted_price: int = 0

class PricelistCreate(PricelistBase):
    pass

class PricelistUpdate(BaseModel):
    unit_price: Optional[int] = None
    selling_price: Optional[int] = None
    discounted_price: Optional[int] = None

class PricelistResponse(PricelistBase, BaseSchema):
    id: int

    class Config:
        from_attributes = True
