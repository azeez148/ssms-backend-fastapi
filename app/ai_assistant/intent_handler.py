from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from .models import ExtractedEntities, ChatResponse, ConversationContext
from .nlp_engine import NLPEngine
from app.models.product import Product
from app.models.order import Order
from app.schemas.order import OrderCreate
from app.services.product import get_products_by_category
from app.core.database import get_db

class IntentHandler:
    def __init__(self, db: Session):
        self.db = db

    async def check_product_availability(
        self, product_name: str, size: Optional[str]
    ) -> Tuple[Optional[Product], List[Product]]:
        """Check if product is available and return related products."""
        # Query for exact match
        query = self.db.query(Product)
        if product_name:
            query = query.filter(Product.name.ilike(f"%{product_name}%"))
        if size:
            query = query.filter(Product.size == size)
        
        product = query.first()
        
        # Get related products using AI-powered similarity
        related_products = []
        if not product and product_name:
            # Get all products
            all_products = self.db.query(Product).all()
            
            # Use NLP engine to find similar products
            nlp = NLPEngine()
            product_prompt = f"""
            Find products similar to: {product_name}
            Consider these aspects:
            - Same sport/team
            - Similar type (jersey, boots, etc.)
            - Similar price range
            - Similar target audience
            
            Products to compare: {[p.name for p in all_products]}
            
            Return only the names of the 5 most similar products.
            """
            
            similar_names = nlp.text_generator(
                product_prompt,
                max_length=128
            )[0]['generated_text'].strip().split('\n')
            
            # Get actual products from suggested names
            for name in similar_names[:5]:
                similar_product = self.db.query(Product).filter(
                    Product.name.ilike(f"%{name.strip()}%")
                ).first()
                if similar_product:
                    related_products.append(similar_product)
        
        return product, related_products

    async def create_order(
        self, customer_id: int, product_id: int, quantity: int = 1
    ) -> Order:
        """Create a new order in the database."""
        order_data = OrderCreate(
            customer_id=customer_id,
            product_id=product_id,
            quantity=quantity,
            status="pending"
        )
        
        # Create order using existing order service
        order = Order(**order_data.dict())
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        
        return order

    async def handle_intent(
        self, entities: ExtractedEntities, context: ConversationContext
    ) -> ChatResponse:
        """Handle the extracted intent and return appropriate response."""
        if not entities.product_name:
            return ChatResponse(
                message="I couldn't understand which product you're looking for. Could you please specify the product name?",
                success=False,
                needs_clarification=True
            )
        
        # Check product availability
        product, related_products = await self.check_product_availability(
            entities.product_name, entities.size
        )
        
        if product:
            if product.stock_quantity >= (entities.quantity or 1):
                message = f"Yes, {product.name} is available in size {product.size} for ₹{product.price}. Would you like to place an order?"
                return ChatResponse(
                    message=message,
                    success=True,
                    product_found=True,
                    extracted_info=entities
                )
            else:
                message = f"Sorry, {product.name} is currently out of stock in size {product.size}."
                if related_products:
                    message += " Here are some similar products you might like:"
                return ChatResponse(
                    message=message,
                    success=True,
                    product_found=False,
                    suggested_products=[p.dict() for p in related_products]
                )
        else:
            message = f"I couldn't find exactly what you're looking for."
            if related_products:
                message += " Here are some similar products you might like:"
            return ChatResponse(
                message=message,
                success=True,
                product_found=False,
                suggested_products=[p.dict() for p in related_products]
            )