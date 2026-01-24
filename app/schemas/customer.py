from pydantic import BaseModel
from typing import Optional
from app.schemas.base import BaseSchema

class CustomerBase(BaseModel):
    name: str
    address: Optional[str] = None
    mobile: str
    email: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    shop_id: Optional[int] = None

    class Config:
        from_attributes = True

    @property
    def normalized_email(self) -> Optional[str]:
        """Return None if email is empty string or None, otherwise return the email"""
        return self.email if self.email and self.email.strip() else None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    pass

class CustomerResponse(CustomerBase, BaseSchema):
    id: int
