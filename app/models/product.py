from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.product_size import ProductSize

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    description = Column(String)
    unit_price = Column(Integer)  # Changed to Integer as per Java model
    selling_price = Column(Integer)  # Changed to Integer as per Java model
    is_active = Column(Boolean, default=False, nullable=False)  # Matches Java default
    can_listed = Column(Boolean, default=False, nullable=False)  # Matches Java default
    
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")
    
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
