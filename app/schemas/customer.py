from pydantic import BaseModel
from typing import Optional

class CustomerBase(BaseModel):
    name: str
    address: Optional[str] = None
    mobile: str
    email: Optional[str] = None

    class Config:
        from_attributes = True

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int
