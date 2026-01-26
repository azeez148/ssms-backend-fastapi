from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime
from app.models.event import EventOfferType, RateType
from app.schemas.base import BaseSchema

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
    code: str = ""
    class Config:
        from_attributes = True

class EventOfferCreate(EventOfferBase):
    pass

class EventOfferResponse(BaseSchema):
    id: int
    name: str
    description: Optional[str] = None
    type: EventOfferType
    is_active: bool
    start_date: datetime
    end_date: datetime
    rate_type: RateType
    rate: int
    product_ids: List[int] = []
    category_ids: List[int] = []
    code: Optional[str] = None

    class Config:
        from_attributes = True

    @field_validator('product_ids', 'category_ids', mode='before')
    @classmethod
    def split_string(cls, v):
        if isinstance(v, str):
            if not v:
                return []
            return [int(x) for x in v.split(',')]
        return v

class EventOfferInDB(EventOfferBase):
    id: int

class EventOfferUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    is_active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    rate_type: Optional[str] = None
    rate: Optional[int] = None
    product_ids: Optional[List[int]] = None
    category_ids: Optional[List[int]] = None
    code: Optional[str] = None

class UpdateProductOfferRequest(BaseModel):
    product_ids: List[int]
    offer_id: Optional[int]
