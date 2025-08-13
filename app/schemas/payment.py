from pydantic import BaseModel
from typing import Optional
from app.schemas.base import BaseSchema

class PaymentTypeBase(BaseModel):
    name: str
    description: Optional[str] = None

class PaymentTypeCreate(PaymentTypeBase):
    pass

class PaymentTypeInDB(PaymentTypeBase):
    id: int
    
    class Config:
        orm_mode = True

class PaymentTypeResponse(PaymentTypeInDB, BaseSchema):
    pass
