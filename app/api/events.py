from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.event import EventOfferCreate, EventOfferResponse
from app.services.event import EventOfferService

router = APIRouter()
event_offer_service = EventOfferService()

@router.post("/create", response_model=EventOfferResponse)
async def create_event_offer(
    event_offer: EventOfferCreate,
    db: Session = Depends(get_db)
):
    return event_offer_service.create_event_offer(db, event_offer)
