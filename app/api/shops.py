from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.shop import ShopCreate, ShopResponse
from app.services.shop import ShopService
from app.api.auth import check_admin_role, get_current_active_user
from app.models.user import User

router = APIRouter()
shop_service = ShopService()

@router.post("/addShop", response_model=ShopResponse)
async def add_shop(
    shop: ShopCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_role)
):
    return shop_service.create_shop(db, shop)

@router.get("/all", response_model=List[ShopResponse])
async def get_all_shops(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from app.schemas.enums import UserRole
    if current_user.role == UserRole.ADMINISTRATOR:
        return shop_service.get_all_shops(db)

    return [shop for shop in current_user.shops]
