from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Category(BaseModel):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    description = Column(String)
    
    products = relationship("Product", back_populates="category")
    attributes = relationship("Attribute", back_populates="category")  # From the Java model
