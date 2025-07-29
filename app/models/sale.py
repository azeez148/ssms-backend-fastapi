from sqlalchemy import Column, Integer, Float, ForeignKey, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String)
    customer_address = Column(String)
    customer_mobile = Column(String)
    customer_email = Column(String, nullable=True)
    date = Column(String)  # Keep as string to match Java model
    total_quantity = Column(Integer)
    total_price = Column(Float)
    payment_reference_number = Column(String, nullable=True)
    
    payment_type_id = Column(Integer, ForeignKey("payment_types.id"))
    payment_type = relationship("PaymentType")
    
    delivery_type_id = Column(Integer, ForeignKey("delivery_types.id"))
    delivery_type = relationship("DeliveryType")
    
    shop_id = Column(Integer, ForeignKey("shops.id"))
    shop = relationship("Shop", back_populates="sales")
    
    sale_items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")

class SaleItem(Base):
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
