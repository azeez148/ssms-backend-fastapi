from pydantic import BaseModel
from typing import Optional

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class CategoryCreate(CategoryBase):
    pass

class CategoryInDB(CategoryBase):
    id: int

class CategoryResponse(CategoryInDB):
    pass

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryInDB(CategoryBase):
    id: int
    
    class Config:
        orm_mode = True

class CategoryResponse(CategoryInDB):
    pass
