from pydantic import BaseModel
from typing import List, Optional
from .shop import ShopResponse
from .vendor import VendorResponse

class PurchaseItemBase(BaseModel):
    product_id: int
    product_name: str
    product_category: str
    size: str
    quantity_available: int
    quantity: int
    purchase_price: float
    total_price: float

    class Config:
        from_attributes = True

class PurchaseItemCreate(PurchaseItemBase):
    pass

class PurchaseItemResponse(PurchaseItemBase):
    id: int

class PurchaseBase(BaseModel):
    date: str
    total_quantity: int
    total_price: float
    payment_type_id: int
    payment_reference_number: str
    delivery_type_id: int
    vendor_id: int

    class Config:
        from_attributes = True

class PurchaseCreate(PurchaseBase):
    purchase_items: List[PurchaseItemCreate]
    shop_ids: List[int]

class PurchaseResponse(PurchaseBase):
    id: int
    purchase_items: List[PurchaseItemResponse]
    shops: List[ShopResponse]
    vendor: VendorResponse
