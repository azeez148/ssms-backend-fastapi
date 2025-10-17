from pydantic import BaseModel
from typing import Optional
from app.schemas.base import BaseSchema

class DeliveryTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    charge: int=0

class DeliveryTypeCreate(DeliveryTypeBase):
    pass

class DeliveryTypeInDB(DeliveryTypeBase):
    id: int
    
    class Config:
        orm_mode = True

class DeliveryTypeResponse(DeliveryTypeInDB, BaseSchema):
    pass
