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
    whatsapp_group_link: Optional[str] = None
    instagram_link: Optional[str] = None
    website_link: Optional[str] = None

class ShopCreate(ShopBase):
    pass

class ShopInDB(ShopBase):
    id: int
    
    class Config:
        from_attributes = True

class ShopResponse(ShopInDB):
    pass
