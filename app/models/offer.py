from sqlalchemy import Column, Integer, String, Boolean, Date, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    discount_type = Column(String)
    discount_value = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True, nullable=False)
    products = relationship("Product", secondary="offer_products", back_populates="offers")

offer_products = Table(
    "offer_products",
    Base.metadata,
    Column("offer_id", Integer, ForeignKey("offers.id"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
)
