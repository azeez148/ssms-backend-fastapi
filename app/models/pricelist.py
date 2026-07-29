from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Pricelist(BaseModel):
    __tablename__ = "pricelists"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id"), unique=True)
    unit_price = Column(Integer, default=0)
    selling_price = Column(Integer, default=0)
    discounted_price = Column(Integer, default=0)

    category = relationship("Category")
