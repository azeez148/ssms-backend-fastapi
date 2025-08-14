from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.product_size import ProductSize
from app.core.database import Base

class Product(BaseModel):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    description = Column(String)
    unit_price = Column(Integer)  # Changed to Integer as per Java model
    selling_price = Column(Integer)  # Changed to Integer as per Java model
    is_active = Column(Boolean, default=False, nullable=False)  # Matches Java default
    can_listed = Column(Boolean, default=False, nullable=False)  # Matches Java default
    image_url = Column(String, nullable=True)
    
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")

    offer_id = Column(Integer, ForeignKey("event_offers.id"), nullable=True)
    offer = relationship("EventOffer", back_populates="products")
    discounted_price = Column(Integer, nullable=True)
    offer_price = Column(Integer, nullable=True)
    offer_name = Column(String, nullable=True)

    # Size map is handled as a separate table in Java using @ElementCollection
    size_map = relationship(
        ProductSize,  # Direct class reference instead of string
        cascade="all, delete-orphan",
        backref="product",
        lazy="joined"  # This will load the sizes eagerly with the product
    )
    shops = relationship("Shop", secondary="shop_products", back_populates="products")


shop_products = Table(
    "shop_products",
    Base.metadata,
    Column("shop_id", Integer, ForeignKey("shops.id"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
)
