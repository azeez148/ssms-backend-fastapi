from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.shop import ShopCreate, ShopResponse
from app.services.shop import ShopService

router = APIRouter()
shop_service = ShopService()

@router.post("/addShop", response_model=ShopResponse)
async def add_shop(
    shop: ShopCreate,
    db: Session = Depends(get_db)
):
    return shop_service.create_shop(db, shop)

@router.get("/all", response_model=List[ShopResponse])
async def get_all_shops(db: Session = Depends(get_db)):
    return shop_service.get_all_shops(db)

# PUT and DELETE endpoints can be added similarly when needed.
@router.put("/{shop_id}", response_model=ShopResponse)
async def update_shop(
    shop_id: int,
    shop: ShopCreate,
    db: Session = Depends(get_db)
):
    return shop_service.update_shop(db, shop_id, shop)
