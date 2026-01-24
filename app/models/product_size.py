from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class ProductSize(BaseModel):
    __tablename__ = "product_sizes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=True)
    size = Column(String)  # This is the key in the Java Map
    quantity = Column(Integer)  # This is the value in the Java Map
