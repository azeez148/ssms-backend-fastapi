from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.delivery import DeliveryTypeCreate, DeliveryTypeResponse
from app.services.delivery import DeliveryTypeService

router = APIRouter()
delivery_type_service = DeliveryTypeService()

@router.post("/addDeliveryType", response_model=DeliveryTypeResponse)
async def add_delivery_type(
    delivery_type: DeliveryTypeCreate,
    db: Session = Depends(get_db)
):
    return delivery_type_service.create_delivery_type(db, delivery_type)

@router.get("/all", response_model=List[DeliveryTypeResponse])
async def get_all_delivery_types(db: Session = Depends(get_db)):
    return delivery_type_service.get_all_delivery_types(db)
