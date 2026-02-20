from pydantic import BaseModel
from typing import Optional
from app.schemas.base import BaseSchema

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True

class CategoryCreate(CategoryBase):
    pass


class CategoryInDB(CategoryBase):
    id: int
    
    class Config:
        orm_mode = True

class CategoryResponse(CategoryInDB, BaseSchema):
    pass