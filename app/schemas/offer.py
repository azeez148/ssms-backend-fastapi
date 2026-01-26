from pydantic import BaseModel
from typing import List, Optional

class UpdateProductOfferRequest(BaseModel):
    product_ids: List[int]
    offer_id: Optional[int]
