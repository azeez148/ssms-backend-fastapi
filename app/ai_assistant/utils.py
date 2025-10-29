from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.product import Product
from app.core.database import get_db

def get_similar_products(db: Session, product: Product, limit: int = 5) -> List[Product]:
    """Find similar products based on category and attributes."""
    return db.query(Product)\
        .filter(Product.category_id == product.category_id)\
        .filter(Product.id != product.id)\
        .limit(limit)\
        .all()

def format_product_message(product: Product, quantity: Optional[int] = 1) -> str:
    """Format product information into a readable message."""
    return f"{product.name} (Size: {product.size}) - ₹{product.price} x {quantity}"

def format_suggestions_message(products: List[Product]) -> str:
    """Format a list of suggested products into a readable message."""
    if not products:
        return "No similar products found."
    
    message = "You might be interested in these similar products:\n"
    for idx, product in enumerate(products, 1):
        message += f"{idx}. {format_product_message(product)}\n"
    return message