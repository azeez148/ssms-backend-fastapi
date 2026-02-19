from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.purchase import shop_purchases

class Shop(BaseModel):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    addressLine1 = Column(String)
    addressLine2 = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    zipcode = Column(String)
    mobileNumber = Column(String)
    email = Column(String)
    whatsapp_group_link = Column(String, nullable=True)
    instagram_link = Column(String, nullable=True)
    website_link = Column(String, nullable=True)
    
    sales = relationship("Sale", back_populates="shop")
    purchases = relationship("Purchase", secondary=shop_purchases, back_populates="shops")
    products = relationship("Product", secondary="shop_products", back_populates="shops")
    users = relationship("User", back_populates="shop")
