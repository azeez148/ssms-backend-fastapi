from sqlalchemy import Column, Integer, Float, ForeignKey, String, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.schemas.enums import SaleStatus

class Sale(BaseModel):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(String)  # Keep as string to match Java model
    total_quantity = Column(Integer)
    total_price = Column(Float)
    payment_reference_number = Column(String, nullable=True)
    
    payment_type_id = Column(Integer, ForeignKey("payment_types.id"))
    payment_type = relationship("PaymentType")
    
    delivery_type_id = Column(Integer, ForeignKey("delivery_types.id"))
    delivery_type = relationship("DeliveryType")

    customer_id = Column(Integer, ForeignKey("customers.id"))
    customer = relationship("Customer", back_populates="sales")
    
    shop_id = Column(Integer, ForeignKey("shops.id"))
    shop = relationship("Shop", back_populates="sales")
    
    sale_items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    status = Column(Enum(SaleStatus), default=SaleStatus.OPEN, nullable=False)

class SaleItem(BaseModel):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer)  # Not a foreign key as per Java model
    product_name = Column(String)
    product_category = Column(String)
    size = Column(String)
    quantity_available = Column(Integer)
    quantity = Column(Integer)
    sale_price = Column(Float)
    total_price = Column(Float)
    
    sale_id = Column(Integer, ForeignKey("sales.id"))
    sale = relationship("Sale", back_populates="sale_items")
