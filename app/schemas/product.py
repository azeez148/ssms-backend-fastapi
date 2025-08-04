from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from typing_extensions import Annotated

from app.schemas.category import CategoryBase

class ProductSizeBase(BaseModel):
    size: str
    quantity: int

    class Config:
        from_attributes = True

class ProductSizeCreate(ProductSizeBase):
    pass

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    unit_price: Annotated[int, Field(gt=0)]  # Changed to int as per Java model
    selling_price: Annotated[int, Field(gt=0)]  # Changed to int as per Java model
    category_id: int
    is_active: bool = False  # Changed default to match Java
    can_listed: bool = False  # Changed default to match Java
    size_map: Optional[List[ProductSizeBase]] = None
    category: CategoryBase
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    unit_price: Annotated[int, Field(gt=0)]  # Changed to int
    selling_price: Annotated[int, Field(gt=0)]  # Changed to int
    is_active: bool
    can_listed: bool
    size_map: Optional[List[ProductSizeBase]] = None

    class Config:
        from_attributes = True

class ProductInDB(ProductBase):
    id: int

class ProductResponse(ProductInDB):
    pass

class UpdateSizeMapRequest(BaseModel):
    product_id: int
    size_map: Dict[str, int]

class ProductFilterRequest(BaseModel):
    category_id: Optional[int] = None
    product_type_filter: Optional[str] = None
