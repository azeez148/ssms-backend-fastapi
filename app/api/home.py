from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from pathlib import Path
from fastapi.responses import FileResponse
from typing import List

from app.core.database import get_db
from app.schemas.home import HomeResponse, OfferResponse
from app.schemas.sale import SaleCreate, SaleResponse
from app.schemas.stock import StockRequest, StockResponse
from app.services.home import HomeService
from app.services.stock import StockService
from app.services.sale import SaleService

router = APIRouter()
home_service = HomeService()
sale_service = SaleService()

@router.get("/all", response_model=HomeResponse)
async def get_home_data(db: Session = Depends(get_db)):
    return home_service.get_home_data(db)

@router.get("/offers", response_model=List[OfferResponse])
async def get_active_offers(db: Session = Depends(get_db)):
    return home_service.get_active_offers(db)

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