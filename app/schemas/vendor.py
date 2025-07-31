from pydantic import BaseModel
from typing import Optional

class VendorBase(BaseModel):
    name: str
    address: Optional[str] = None
    mobile: str
    email: Optional[str] = None

    class Config:
        from_attributes = True

class VendorCreate(VendorBase):
    pass

class VendorUpdate(VendorBase):
    pass

class VendorResponse(VendorBase):
    id: int
