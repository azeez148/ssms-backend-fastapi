from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel
from datetime import datetime

class User(BaseModel):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    mobile = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    role = Column(String, default="customer")
    customer_id = Column(Integer, ForeignKey("customers.id"), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with Customer
    customer = relationship("Customer", back_populates="user")