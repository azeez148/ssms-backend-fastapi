from sqlalchemy import Column, Integer, Float, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Purchase(BaseModel):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(String)  # could be Date type if desired

    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    vendor = relationship("Vendor", back_populates="purchases")

    purchase_items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")

    total_quantity = Column(Integer)
    total_price = Column(Float)

    payment_type_id = Column(Integer, ForeignKey("payment_types.id"))
    payment_type = relationship("PaymentType")

    payment_reference_number = Column(String)

    delivery_type_id = Column(Integer, ForeignKey("delivery_types.id"))
    delivery_type = relationship("DeliveryType")

    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=True)
    shop = relationship("Shop", back_populates="purchases")

class PurchaseItem(BaseModel):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer)
    product_name = Column(String)
    product_category = Column(String)
    size = Column(String)
    quantity_available = Column(Integer)
    quantity = Column(Integer)
    purchase_price = Column(Float)
    total_price = Column(Float)

    purchase_id = Column(Integer, ForeignKey("purchases.id"))
    purchase = relationship("Purchase", back_populates="purchase_items")
