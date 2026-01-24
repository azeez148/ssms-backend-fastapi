from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from .base import BaseModel
from datetime import datetime
from app.schemas.enums import UserRole
from app.core.database import Base

user_shops = Table(
    "user_shops",
    Base.metadata,
    Column("user_id", String, ForeignKey("users.id"), primary_key=True),
    Column("shop_id", Integer, ForeignKey("shops.id"), primary_key=True),
)

class User(BaseModel):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    mobile = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    customer_id = Column(Integer, ForeignKey("customers.id"), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    role = Column(Enum(UserRole), default=UserRole.STAFF, nullable=False)

    # Relationship with Customer
    customer = relationship("Customer", back_populates="user")
    shops = relationship("Shop", secondary=user_shops, backref="users")