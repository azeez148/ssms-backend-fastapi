from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from .payment import PaymentTypeResponse
from .delivery import DeliveryTypeResponse
from .customer import CustomerResponse
from app.schemas.base import BaseSchema
from app.schemas.enums import SaleStatus

class SaleItemBase(BaseModel):
    product_id: int
    product_name: str
    product_category: str
    size: str
    quantity_available: int
    quantity: int
    sale_price: float
    total_price: float

    class Config:
        from_attributes = True

class SaleItemCreate(SaleItemBase):
    pass

class SaleItemInDB(SaleItemBase):
    id: int
    sale_id: int

class SaleItemResponse(SaleItemInDB, BaseSchema):
    pass

class SaleBase(BaseModel):
    date: str
    total_quantity: int
    total_price: float
    payment_type_id: int
    payment_reference_number: Optional[str] = None
    delivery_type_id: int
    shop_id: int
    customer_id: int
    status: Optional[SaleStatus] = SaleStatus.OPEN

    class Config:
        from_attributes = True

class SaleCreate(SaleBase):
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    customer_mobile: Optional[str] = None
    customer_email: Optional[str] = None
    sale_items: List[SaleItemCreate]

class SaleInDB(SaleBase):
    id: int
    sale_items: List[SaleItemResponse]
    payment_type: Optional[PaymentTypeResponse] = None
    delivery_type: Optional[DeliveryTypeResponse] = None
    customer: Optional[CustomerResponse] = None
    status: SaleStatus

class SaleResponse(SaleInDB, BaseSchema):
    pass
