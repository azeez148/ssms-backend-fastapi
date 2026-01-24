from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
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
    parent_id = Column(Integer, ForeignKey("shops.id"), nullable=True)
    
    parent = relationship("Shop", remote_side=[id], backref="children")
    sales = relationship("Sale", back_populates="shop")
    purchases = relationship("Purchase", back_populates="shop")
    products = relationship("Product", secondary="shop_products", back_populates="shops")
