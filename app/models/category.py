from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Category(BaseModel):
    __tablename__ = "categories"

    id = Column(Integer, Sequence('categories_id_seq'), primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    size_map = Column(String, nullable=True)
    
    products = relationship("Product", back_populates="category")
    attributes = relationship("Attribute", back_populates="category")  # From the Java model
