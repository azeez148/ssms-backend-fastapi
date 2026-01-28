from pydantic import BaseModel
from typing import Optional, List
from app.schemas.base import BaseSchema

class TagBase(BaseModel):
    name: str
    description: Optional[str] = None

class TagCreate(TagBase):
    pass

class TagUpdate(TagBase):
    id: int

class TagResponse(TagBase, BaseSchema):
    id: int

    class Config:
        from_attributes = True

class TagMapRequest(BaseModel):
    productIds: List[int]
    tagIds: List[int]
