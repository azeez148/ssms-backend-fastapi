from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.payment import PaymentTypeCreate, PaymentTypeResponse
from app.services.payment import PaymentTypeService

router = APIRouter()
payment_type_service = PaymentTypeService()

@router.post("/addPaymentType", response_model=PaymentTypeResponse)
async def add_payment_type(
    payment_type: PaymentTypeCreate,
    db: Session = Depends(get_db)
):
    return payment_type_service.create_payment_type(db, payment_type)

@router.get("/all", response_model=List[PaymentTypeResponse])
async def get_all_payment_types(db: Session = Depends(get_db)):
    return payment_type_service.get_all_payment_types(db)
