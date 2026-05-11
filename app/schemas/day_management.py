from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from app.schemas.base import BaseSchema

# Expense Schemas
class ExpenseBase(BaseModel):
    description: str
    amount: float

class ExpenseCreate(ExpenseBase):
    day_id: Optional[int] = None
    shop_id: Optional[int] = None

class Expense(ExpenseBase, BaseSchema):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# Day Schemas
class DayBase(BaseModel):
    opening_balance: float

class DayCreate(DayBase):
    shop_id: Optional[int] = 1

class EndDayRequest(BaseModel):
    closing_balance: float          # actual cash counted by staff
    variance_reason: Optional[str] = None

class Day(DayBase, BaseSchema):
    id: int
    shop_id: Optional[int] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    closing_balance: Optional[float] = None
    total_expense: Optional[float] = None
    cash_in_hand: Optional[float] = None
    cash_in_account: Optional[float] = None
    total_sales: Optional[float] = None
    total_cash_sales: Optional[float] = None
    total_account_sales: Optional[float] = None
    variance: Optional[float] = None
    variance_reason: Optional[str] = None
    expenses: List[Expense] = []

    class Config:
        from_attributes = True

# Day Summary Schema — full status for a day
class DaySummary(BaseModel):
    day_id: int
    date: Optional[str] = None
    shop_id: Optional[int] = None
    shop_name: Optional[str] = None
    opening_balance: float
    total_expense: float
    expenses: List[Expense] = []
    total_sales: float
    total_cash_sales: float
    total_account_sales: float
    cash_in_hand: float             # expected cash (calculated)
    cash_in_account: float          # total non-cash sales
    closing_balance: Optional[float] = None   # actual cash counted
    variance: Optional[float] = None          # closing_balance - cash_in_hand
    variance_reason: Optional[str] = None
    day_started: bool
    day_ended: bool
    start_time: datetime
    end_time: Optional[datetime] = None
    message: Optional[str] = None

    class Config:
        from_attributes = True


class StatusResponse(BaseModel):
    day_started: bool
    active_day: Optional[Day] = None

class ShopStatusResponse(BaseModel):
    shop_id: int
    shop_name: str
    day_started: bool
    day_ended: bool
    active_day: Optional[Day] = None