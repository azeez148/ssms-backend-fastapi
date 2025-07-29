from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.purchase import PurchaseCreate, PurchaseResponse
from app.services.purchase import PurchaseService

router = APIRouter()
purchase_service = PurchaseService()

@router.post("/addPurchase", response_model=PurchaseResponse)
async def add_purchase(
    purchase: PurchaseCreate,
    db: Session = Depends(get_db)
):
    return purchase_service.create_purchase(db, purchase)

@router.get("/all", response_model=List[PurchaseResponse])
async def get_all_purchases(db: Session = Depends(get_db)):
    return purchase_service.get_all_purchases(db)
