from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    supplier_name = Column(String)
    supplier_address = Column(String)
    supplier_mobile = Column(String)
    supplier_email = Column(String)
    date = Column(String)
    total_quantity = Column(Integer)
    total_price = Column(Float)
    payment_reference_number = Column(String)
    
    payment_type_id = Column(Integer, ForeignKey("payment_types.id"))
    payment_type = relationship("PaymentType")
    
    delivery_type_id = Column(Integer, ForeignKey("delivery_types.id"))
    delivery_type = relationship("DeliveryType")
    
    # Optional shop relationship - can be null
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=True)
    shop = relationship("Shop", back_populates="purchases")
    
    purchase_items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")

class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer)  # Not a foreign key as per Java model
    product_name = Column(String)
    product_category = Column(String)
    size = Column(String)
    quantity_available = Column(Integer)
    quantity = Column(Integer)
    purchase_price = Column(Float)
    total_price = Column(Float)
    
    purchase_id = Column(Integer, ForeignKey("purchases.id"))
    purchase = relationship("Purchase", back_populates="purchase_items")
