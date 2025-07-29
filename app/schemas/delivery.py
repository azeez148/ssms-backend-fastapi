from pydantic import BaseModel
from typing import Optional

class DeliveryTypeBase(BaseModel):
    name: str
    description: Optional[str] = None

class DeliveryTypeCreate(DeliveryTypeBase):
    pass

class DeliveryTypeInDB(DeliveryTypeBase):
    id: int
    
    class Config:
        orm_mode = True

class DeliveryTypeResponse(DeliveryTypeInDB):
    pass
