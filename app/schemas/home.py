from pydantic import BaseModel
from typing import List
from app.schemas.product import ProductResponse

class HomeResponse(BaseModel):
    products: List[ProductResponse]
    
    class Config:
        orm_mode = True
