from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class PaymentType(Base):
    __tablename__ = "payment_types"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    description = Column(String)
    
    sales = relationship("Sale", back_populates="payment_type")
