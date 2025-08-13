from pydantic import BaseModel
from typing import List
from app.schemas.product import ProductResponse
from app.schemas.base import BaseSchema

class HomeResponse(BaseSchema):
    products: List[ProductResponse]
    
    class Config:
        orm_mode = True
