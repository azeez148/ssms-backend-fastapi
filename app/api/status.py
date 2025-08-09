from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.status import StatusResponse
from app.services.day_management import DayManagementService

router = APIRouter()
day_management_service = DayManagementService()

@router.get("/", response_model=StatusResponse)
def get_status(db: Session = Depends(get_db)):
    active_day = day_management_service.get_active_day(db)
    if active_day:
        return StatusResponse(dayStarted=True, opening_balance=active_day.opening_balance)
    else:
        return StatusResponse(dayStarted=False, opening_balance=0)
