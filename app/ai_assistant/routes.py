from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from .models import ChatResponse, ConversationContext
from .nlp_engine import NLPEngine
from .intent_handler import IntentHandler
from app.core.database import get_db
from app.api.auth import get_current_user
from app.schemas.user import User

router = APIRouter()
nlp_engine = NLPEngine()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    message: str,
    customer_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process a chat message and return an appropriate response.
    """
    # Extract entities and intent from message
    extracted_info = nlp_engine.analyze_message(message)
    
    # Initialize conversation context
    context = ConversationContext(
        customer_id=customer_id or current_user.id,
        needs_clarification=False,
        missing_fields=[]
    )
    
    # Handle the intent
    intent_handler = IntentHandler(db)
    response = await intent_handler.handle_intent(extracted_info, context)
    
    return response

@router.post("/place-order")
async def place_order(
    product_id: int,
    quantity: int = 1,
    size: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Place an order for a product identified in the chat.
    """
    intent_handler = IntentHandler(db)
    try:
        order = await intent_handler.create_order(
            customer_id=current_user.id,
            product_id=product_id,
            quantity=quantity
        )
        return {"message": "Order placed successfully", "order_id": order.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))