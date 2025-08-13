from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func
from app.core.database import Base

class BaseModel(Base):
    __abstract__ = True

    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
