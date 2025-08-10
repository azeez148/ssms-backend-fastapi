from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.day_management import (
    DayCreate,
    Day,
    ExpenseCreate,
    Expense,
    DaySummary,
    StatusResponse
)
from app.services.day_management import DayManagementService

router = APIRouter()
day_management_service = DayManagementService()

@router.post("/startDay", response_model=Day)
def start_day(day: DayCreate, db: Session = Depends(get_db)):
    try:
        return day_management_service.start_day(db, day)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/addExpense", response_model=Expense)
def add_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    try:
        return day_management_service.add_expense(db, expense)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/expenses/{day_id}", response_model=List[Expense])
def get_expenses(day_id: int, db: Session = Depends(get_db)):
    return day_management_service.get_expenses_for_day(db, day_id)

@router.post("/endDay/{day_id}", response_model=DaySummary)
def end_day(day_id: int, cash_in_hand: float, cash_in_account: float, db: Session = Depends(get_db)):
    try:
        day_management_service.end_day(db, day_id, cash_in_hand, cash_in_account)
        return day_management_service.get_day_summary(db, day_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/activeDay", response_model=Day)
def get_active_day(db: Session = Depends(get_db)):
    active_day = day_management_service.get_active_day(db)
    if not active_day:
        raise HTTPException(status_code=404, detail="No active day found.")
    return active_day

@router.get("/today", response_model=StatusResponse)
def get_status(db: Session = Depends(get_db)):
    active_day = day_management_service.get_active_day(db)
    if active_day:
        return StatusResponse(day_started=True, active_day=active_day)
    else:
        return StatusResponse(day_started=False, active_day=None)
