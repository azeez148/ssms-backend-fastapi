from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.purchase import shop_purchases

class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    contact = Column(String)
    
    sales = relationship("Sale", back_populates="shop")
    purchases = relationship("Purchase", secondary=shop_purchases, back_populates="shops")
    products = relationship("Product", secondary="shop_products", back_populates="shops")
