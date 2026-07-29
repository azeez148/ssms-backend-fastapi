from pydantic import BaseModel
from typing import List, Optional
from app.schemas.product import ProductResponse
from app.schemas.base import BaseSchema
from datetime import datetime
from app.models.event import RateType, EventOfferType


class OfferResponse(BaseSchema):
    id: int
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    rate: int
    rate_type: RateType
    type: EventOfferType

    class Config:
        from_attributes = True


class HomeResponse(BaseSchema):
    products: List[ProductResponse]
    
    class Config:
        from_attributes = True
