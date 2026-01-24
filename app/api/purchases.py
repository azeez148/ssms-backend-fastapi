from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.purchase import PurchaseCreate, PurchaseResponse
from app.services.purchase import PurchaseService
from app.api.auth import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post("/addPurchase", response_model=PurchaseResponse)
async def add_purchase(
    purchase: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from app.schemas.enums import UserRole
    if current_user.role != UserRole.ADMINISTRATOR:
        if purchase.shop_id not in [s.id for s in current_user.shops]:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="You do not have access to this shop")

    purchase_service = PurchaseService()
    return purchase_service.create_purchase(db, purchase)

@router.get("/all", response_model=List[PurchaseResponse])
async def get_all_purchases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    purchase_service = PurchaseService()
    return purchase_service.get_all_purchases(db, current_user)
