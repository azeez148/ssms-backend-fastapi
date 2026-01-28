from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.event import EventOfferCreate, EventOfferResponse, EventOfferUpdate, EventOfferUpdateRequest, UpdateProductOfferRequest
from app.services.event import EventOfferService

router = APIRouter()
event_offer_service = EventOfferService()

@router.post("/create", response_model=EventOfferResponse)
async def create_event_offer(
    event_offer: EventOfferCreate,
    db: Session = Depends(get_db)
):
    return event_offer_service.create_event_offer(db, event_offer)

@router.get("/all", response_model=List[EventOfferResponse])
async def get_all_event_offers(db: Session = Depends(get_db)):
    return event_offer_service.get_all_event_offers(db)

@router.post("/update/{offer_id}", response_model=EventOfferResponse)
async def update_event_offer(
    offer_id: int,
    payload: EventOfferUpdateRequest,
    db: Session = Depends(get_db)
):
    updated_offer = event_offer_service.update_event_offer(
        db, offer_id, payload.offer_update
    )
    if not updated_offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return updated_offer

@router.post("/updateOffer")
async def update_product_offer(
    request: UpdateProductOfferRequest,
    db: Session = Depends(get_db)
):
    try:
        return event_offer_service.update_product_offer(db, request.product_ids, request.offer_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.post("/set_active_status", response_model=EventOfferResponse)
async def set_event_offer_active_status(
    offer_id: int,
    is_active: bool,
    db: Session = Depends(get_db)
):
    updated_offer = event_offer_service.set_event_offer_active_status(db, offer_id, is_active)
    if not updated_offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return updated_offer
