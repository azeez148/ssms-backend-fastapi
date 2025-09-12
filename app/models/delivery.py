from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class DeliveryType(BaseModel):
    __tablename__ = "delivery_types"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    description = Column(String)
    charge = Column(Integer, nullable=False, default=0)
    
    sales = relationship("Sale", back_populates="delivery_type")
