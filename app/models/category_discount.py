from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class CategoryDiscount(BaseModel):
    __tablename__ = "category_discounts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id"), unique=True)
    discounted_price = Column(Integer)

    category = relationship("Category")
