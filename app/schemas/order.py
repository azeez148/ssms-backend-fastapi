from pydantic import BaseModel
from typing import List
from datetime import datetime

class OrderItemBase(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float

class OrderItem(OrderItemBase):
    id: str
    order_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrderItemCreate(OrderItemBase):
    pass

class OrderBase(BaseModel):
    total: float
    status: str

class Order(OrderBase):
    id: str
    user_id: str
    date: datetime
    items: List[OrderItem]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]