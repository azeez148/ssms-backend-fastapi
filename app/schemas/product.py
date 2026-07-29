from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Optional, List
from typing_extensions import Annotated
from app.schemas.base import BaseSchema
from app.schemas.category import CategoryInDB
from app.schemas.tag import TagResponse
from app.schemas.shop import ShopResponse, ShopMinimalResponse

class ProductSizeBase(BaseModel):
    size: str
    quantity: int

    model_config = ConfigDict(from_attributes=True)

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
    is_duplicate: bool = False
    parent_product_id: Optional[int] = None
    tags: Optional[List[TagResponse]] = None
    shops: Optional[List[ShopResponse]] = None

    model_config = ConfigDict(from_attributes=True)

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
    shop_ids: Optional[List[int]] = None

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
    shop_ids: Optional[List[int]] = None

    model_config = ConfigDict(from_attributes=True)

class ProductInDB(ProductBase):
    id: int

class ProductResponse(ProductInDB, BaseSchema):
    pass

class ProductMinimalResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    unit_price: int
    selling_price: int
    category_id: int
    is_active: bool
    can_listed: bool
    image_url: Optional[str] = None
    is_duplicate: bool
    parent_product_id: Optional[int] = None
    discounted_price: Optional[int] = None
    category_name: Optional[str] = None
    shops: Optional[List[ShopMinimalResponse]] = None
    is_in_stock: Optional[bool] = None
    offer_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    per_page: int

class ProductMinimalListResponse(BaseModel):
    items: List[ProductMinimalResponse]
    total: int
    page: int
    per_page: int

class ProductHomeMinimalResponse(ProductMinimalResponse):
    size_map: Optional[List[ProductSizeBase]] = None

class ProductHomeMinimalListResponse(BaseModel):
    items: List[ProductHomeMinimalResponse]
    total: int
    page: int
    per_page: int

class UpdateSizeMapRequest(BaseModel):
    product_id: int
    size_map: Dict[str, int]

class ProductFilterRequest(BaseModel):
    category_id: Optional[int] = None
    product_type_filter: Optional[str] = None

class CategoryDiscountRequest(BaseModel):
    category_id: int
    discounted_price: int

class CategoryDiscountResponse(BaseModel):
    id: int
    category_id: int
    discounted_price: int

    model_config = ConfigDict(from_attributes=True)

class CategoryDiscountUpdateRequest(BaseModel):
    category_id: int
    discounted_price: int
    id: int

class ProductTransferRequest(BaseModel):
    product_ids: List[int]
    operation: str  # "copy" or "move"
    destination_shop_id: int
