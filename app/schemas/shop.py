from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from app.schemas.base import BaseSchema

class ShopBase(BaseModel):
    shop_code: Optional[str] = None
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

class ShopResponse(ShopInDB, BaseSchema):
    pass

class ShopMinimalResponse(BaseModel):
    id: int
    name: str
    shop_code: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
