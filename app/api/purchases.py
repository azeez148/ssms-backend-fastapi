from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.purchase import PurchaseCreate, PurchaseResponse
from app.services.purchase import PurchaseService

router = APIRouter()

@router.post("/addPurchase", response_model=PurchaseResponse)
async def add_purchase(
    purchase: PurchaseCreate,
    db: Session = Depends(get_db)
):
    purchase_service = PurchaseService()
    return purchase_service.create_purchase(db, purchase)

@router.get("/all", response_model=List[PurchaseResponse])
async def get_all_purchases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    purchase_service = PurchaseService()
    return purchase_service.get_all_purchases(db, skip=skip, limit=limit)
