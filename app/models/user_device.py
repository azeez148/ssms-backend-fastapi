from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel
from datetime import datetime

class UserDevice(BaseModel):
    __tablename__ = "user_devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    fcm_token = Column(String, unique=True, index=True, nullable=False)
    device_type = Column(String, nullable=True) # e.g., 'android', 'ios'
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="devices")
