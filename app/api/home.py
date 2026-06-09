from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from pathlib import Path
from fastapi.responses import FileResponse
from typing import List, Optional

from app.core.database import get_db
from app.schemas.home import HomeResponse, OfferResponse
from app.schemas.product import ProductMinimalListResponse, ProductResponse
from app.schemas.category import CategoryResponse
from app.schemas.sale import SaleCreate, SaleResponse
from app.schemas.stock import StockRequest, StockResponse
from app.schemas.tag import TagResponse
from app.services.home import HomeService
from app.services.stock import StockService
from app.services.sale import SaleService
from app.services.tag import TagService

router = APIRouter()
home_service = HomeService()
sale_service = SaleService()
tag_service = TagService()

@router.get("/all", response_model=HomeResponse)
async def get_home_data(db: Session = Depends(get_db)):
    return home_service.get_home_data(db)

@router.get("/products", response_model=ProductMinimalListResponse)
async def get_products(db: Session = Depends(get_db), skip: int = 0,
    limit: Optional[int] = 50,
    category_id: Optional[int] = None,
    shop_id: Optional[int] = None,
    search: Optional[str] = None,
    has_image: Optional[bool] = None,
    is_in_stock: Optional[bool] = None,
    has_offer: Optional[bool] = None,
    tag_id: Optional[int] = None,
    sort_by: str = "newest"):
    products, total = home_service.get_products(db, skip=skip,
            limit=limit,
            category_id=category_id,
            shop_id=shop_id,
            search=search,
            has_image=has_image,
            is_in_stock=is_in_stock,
            has_offer=has_offer,
            tag_id=tag_id,
            sort_by=sort_by)

    return {
        "items": products,
        "total": total,
        "page": (skip // (limit or 100)) + 1,
        "per_page": limit or total
    }

@router.get("/offers", response_model=List[OfferResponse])
async def get_active_offers(db: Session = Depends(get_db)):
    return home_service.get_active_offers(db)

@router.get("/weeklyOffers", response_model=List[ProductResponse])
async def get_weekly_offers(db: Session = Depends(get_db)):
    return home_service.get_weekly_offers(db)

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    return home_service.get_categories(db)

@router.get("/search", response_model=ProductMinimalListResponse)
async def search_products(search: str, db: Session = Depends(get_db), skip: int = 0,
    limit: Optional[int] = 50,
    category_id: Optional[int] = None,
    shop_id: Optional[int] = None,
    has_image: Optional[bool] = None,
    is_in_stock: Optional[bool] = None,
    has_offer: Optional[bool] = None,
    tag_id: Optional[int] = None,
    sort_by: str = "newest"):
    products, total = home_service.get_products(db, skip=skip,
            limit=limit,
            category_id=category_id,
            shop_id=shop_id,
            search=search,
            has_image=has_image,
            is_in_stock=is_in_stock,
            has_offer=has_offer,
            tag_id=tag_id,
            sort_by=sort_by)
    return {
        "items": products,
        "total": total,
        "page": (skip // (limit or 100)) + 1,
        "per_page": limit or total
    }

@router.get("/new-arrivals", response_model=List[ProductResponse])
async def get_new_arrivals(db: Session = Depends(get_db)):
    return home_service.get_new_arrivals(db)

@router.get("/offer-products", response_model=List[ProductResponse])
async def get_offer_products(db: Session = Depends(get_db)):
    return home_service.get_offer_products(db)

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = home_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/{product_id}/image")
async def get_product_image(product_id: int):
    image_dir = Path("images/products") / str(product_id)
    
    if not image_dir.exists():
        # Return default image
        return FileResponse("images/notfound.png")
    
    # Return the first image found for the product
    try:
        image_file = next(image_dir.glob("*"))
        return FileResponse(str(image_file))
    except StopIteration:
        return FileResponse("images/notfound.png")

@router.post("/check", response_model=StockResponse)
def check_stock(stock_request: StockRequest, db: Session = Depends(get_db)):
    stock_service = StockService()
    return stock_service.check_stock(db, stock_request)


@router.post("/addSale", response_model=SaleResponse)
async def add_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db)
):
    return sale_service.create_sale(db, sale)

@router.get("/tags", response_model=List[TagResponse])
async def get_tags(db: Session = Depends(get_db)):
    return tag_service.get_all_tags(db)