from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.day_management import (
    DayCreate,
    Day,
    ExpenseCreate,
    Expense,
    DaySummary,
    StatusResponse,
    ShopStatusResponse,
    EndDayRequest
)
from app.services.day_management import DayManagementService
from app.api.auth import get_current_user
from app.models.user import User
from app.models.day_management import Day as DayModel

router = APIRouter()
day_management_service = DayManagementService()

def check_shop_access(current_user: User, shop_id: int):
    if current_user.role != "admin" and current_user.shop_id != shop_id:
        raise HTTPException(status_code=403, detail="You do not have access to this shop's day management.")

@router.post("/startDay", response_model=Day)
def start_day(day: DayCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_shop_access(current_user, day.shop_id)
    try:
        return day_management_service.start_day(db, day)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/addExpense", response_model=Expense)
def add_expense(expense: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        active_day = day_management_service.get_active_day(db, current_user.shop_id)
        if not active_day:
            raise HTTPException(status_code=400, detail="No active day found for your shop.")
        if expense.day_id and expense.day_id != active_day.id:
            raise HTTPException(status_code=403, detail="You can only add expenses to your own shop's active day.")
        shop_id = current_user.shop_id
    else:
        if expense.shop_id:
            shop_id = expense.shop_id
        elif expense.day_id:
            db_day = db.query(DayModel).filter(DayModel.id == expense.day_id).first()
            if not db_day:
                raise HTTPException(status_code=400, detail="Day not found.")
            shop_id = db_day.shop_id
        else:
            raise HTTPException(status_code=400, detail="Admin must provide shop_id or day_id.")
    try:
        return day_management_service.add_expense(db, expense, shop_id=shop_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/expenses/{day_id}", response_model=List[Expense])
def get_expenses(day_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_day = db.query(DayModel).filter(DayModel.id == day_id).first()
    if not db_day:
        raise HTTPException(status_code=404, detail="Day not found.")
    check_shop_access(current_user, db_day.shop_id)
    return day_management_service.get_expenses_for_day(db, day_id)

@router.post("/endDay/{day_id}", response_model=DaySummary)
def end_day(day_id: int, day_data: EndDayRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_day = db.query(DayModel).filter(DayModel.id == day_id).first()
    if not db_day:
        raise HTTPException(status_code=404, detail="Day not found.")
    check_shop_access(current_user, db_day.shop_id)
    try:
        day_management_service.end_day(db, day_id, day_data.closing_balance, day_data.variance_reason)
        return day_management_service.get_day_summary(db, day_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/activeDay", response_model=Day)
def get_active_day(shop_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        shop_id = current_user.shop_id
    elif shop_id is None:
        raise HTTPException(status_code=400, detail="Admin must provide shop_id.")

    active_day = day_management_service.get_active_day(db, shop_id)
    if not active_day:
        raise HTTPException(status_code=404, detail="No active day found for this shop.")
    return active_day

@router.get("/day/{day_id}", response_model=DaySummary)
def get_day_summary(day_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieve full status/summary of a specific day."""
    db_day = db.query(DayModel).filter(DayModel.id == day_id).first()
    if not db_day:
        raise HTTPException(status_code=404, detail="Day not found.")
    check_shop_access(current_user, db_day.shop_id)
    try:
        return day_management_service.get_day_summary(db, day_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/today", response_model=List[ShopStatusResponse])
def get_today_status(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get the day status for all shops (admin) or current shop (staff)."""
    if current_user.role == "admin":
        return day_management_service.get_all_shops_status(db)
    else:
        from app.models.shop import Shop
        shop = db.query(Shop).filter(Shop.id == current_user.shop_id).first()
        today_day = day_management_service.get_today_day(db, current_user.shop_id)
        return [ShopStatusResponse(
            shop_id=current_user.shop_id,
            shop_name=shop.name if shop else "Unknown",
            day_started=today_day is not None,
            day_ended=today_day is not None and today_day.end_time is not None,
            active_day=today_day
        )]
