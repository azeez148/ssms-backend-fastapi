from pydantic import BaseModel, ConfigDict
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
    
    model_config = ConfigDict(from_attributes=True)

class CategoryResponse(CategoryInDB, BaseSchema):
    pass