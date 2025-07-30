from pydantic import BaseModel
from typing import Optional, List

class ShopBase(BaseModel):
    name: str
    addressLine1: str
    addressLine2: str
    city: str
    state: str
    country: str
    zipcode: str
    mobileNumber: str
    email: str

class ShopCreate(ShopBase):
    pass

class ShopInDB(ShopBase):
    id: int
    
    class Config:
        from_attributes = True

class ShopResponse(ShopInDB):
    pass
