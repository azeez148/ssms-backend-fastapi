from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.offer import OfferCreate, OfferResponse, OfferUpdate
from app.services.offer import OfferService

router = APIRouter()
offer_service = OfferService()

@router.post("/add", response_model=OfferResponse)
async def add_offer(
    offer: OfferCreate,
    db: Session = Depends(get_db)
):
    return offer_service.create_offer(db, offer)

@router.get("/all", response_model=List[OfferResponse])
async def get_all_offers(db: Session = Depends(get_db)):
    return offer_service.get_all_offers(db)

@router.post("/update", response_model=OfferResponse)
async def update_offer(
    offer_update: OfferUpdate,
    db: Session = Depends(get_db)
):
    updated_offer = offer_service.update_offer(db, offer_update)
    if not updated_offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return updated_offer

@router.post("/{offer_id}/add_products", response_model=OfferResponse)
async def add_products_to_offer(
    offer_id: int,
    product_ids: List[int],
    db: Session = Depends(get_db)
):
    offer = offer_service.add_products_to_offer(db, offer_id, product_ids)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer
