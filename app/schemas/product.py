from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from typing_extensions import Annotated
from app.schemas.base import BaseSchema
from app.schemas.category import CategoryInDB
from app.schemas.tag import TagResponse

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
    category: CategoryInDB
    image_url: Optional[str] = None
    offer_id: Optional[int] = None
    discounted_price: Optional[int] = None
    offer_price: Optional[int] = None
    offer_name: Optional[str] = None  # Added for offer name
    tags: Optional[List[TagResponse]] = None


    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    unit_price: Annotated[int, Field(gt=0)]  # Changed to int as per Java model
    selling_price: Annotated[int, Field(gt=0)]  # Changed to int as per Java model
    category_id: int
    is_active: bool = False  # Changed default to match Java
    can_listed: bool = False  # Changed default to match Java
    size_map: Optional[List[ProductSizeBase]] = None
    image_url: Optional[str] = None
    offer_id: Optional[int] = None
    discounted_price: Optional[int] = None
    offer_price: Optional[int] = None
    offer_name: Optional[str] = None  # Added for offer name

class ProductUpdate(BaseModel):
    id: int    
    name: str
    description: Optional[str] = None
    unit_price: Annotated[int, Field(gt=0)]  # Changed to int as per Java model
    selling_price: Annotated[int, Field(gt=0)]  # Changed to int as per Java model
    category_id: int
    is_active: bool = False  # Changed default to match Java
    can_listed: bool = False  # Changed default to match Java
    offer_id: Optional[int] = None
    discounted_price: Optional[int] = None
    offer_price: Optional[int] = None
    offer_name: Optional[str] = None  # Added for offer name

    class Config:
        from_attributes = True

class ProductInDB(ProductBase):
    id: int

class ProductResponse(ProductInDB, BaseSchema):
    pass

class UpdateSizeMapRequest(BaseModel):
    product_id: int
    size_map: Dict[str, int]

class ProductFilterRequest(BaseModel):
    category_id: Optional[int] = None
    product_type_filter: Optional[str] = None
