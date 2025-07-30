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
    date = Column(String)  # could be Date type if desired

    purchase_items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")

    total_quantity = Column(Integer)
    total_price = Column(Float)

    payment_type_id = Column(Integer, ForeignKey("payment_types.id"))
    payment_type = relationship("PaymentType")

    payment_reference_number = Column(String)

    delivery_type_id = Column(Integer, ForeignKey("delivery_types.id"))
    delivery_type = relationship("DeliveryType")

class PurchaseItem(Base):
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
