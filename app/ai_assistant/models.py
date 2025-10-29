from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class Intent(str, Enum):
    BUY_PRODUCT = "buy_product"
    CHECK_AVAILABILITY = "check_availability"
    GET_PRICE = "get_price"
    UNKNOWN = "unknown"

class ExtractedEntities(BaseModel):
    product_name: Optional[str]
    size: Optional[str]
    quantity: Optional[int] = 1
    intent: Intent = Intent.UNKNOWN

class ConversationContext(BaseModel):
    customer_id: Optional[int]
    last_product_id: Optional[int]
    last_size: Optional[str]
    last_quantity: Optional[int]
    needs_clarification: bool = False
    missing_fields: List[str] = []

class ChatResponse(BaseModel):
    message: str
    success: bool
    product_found: bool = False
    needs_clarification: bool = False
    suggested_products: Optional[List[dict]] = None
    extracted_info: Optional[ExtractedEntities] = None