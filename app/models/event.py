from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class EventOfferType(enum.Enum):
    event = "event"
    offer = "offer"

class RateType(enum.Enum):
    flat = "flat"
    percentage = "percentage"

class EventOffer(Base):
    __tablename__ = "event_offers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    description = Column(String)
    type = Column(Enum(EventOfferType))
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    rate_type = Column(Enum(RateType))
    rate = Column(Integer)

    products = relationship("Product", back_populates="offer")

    # These are not direct relationships, but rather store the ids
    # We will handle the logic of applying these in the service layer
    product_ids = Column(String)  # Storing as comma-separated string of ids
    category_ids = Column(String) # Storing as comma-separated string of ids
