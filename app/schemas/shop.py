from pydantic import BaseModel
from typing import Optional

class ShopBase(BaseModel):
    name: str
    location: Optional[str] = None
    contact: Optional[str] = None

class ShopCreate(ShopBase):
    pass

class ShopInDB(ShopBase):
    id: int
    
    class Config:
        orm_mode = True

class ShopResponse(ShopInDB):
    pass
