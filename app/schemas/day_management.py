from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
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
    variance: Optional[float] = None
    variance_reason: Optional[str] = None

class DayUpdate(BaseModel):
    closing_balance: float
    total_expense: float
    cash_in_hand: float
    cash_in_account: float
    end_time: datetime

class EndDayRequest(BaseModel):
    closing_balance_actual: float
    variance: float = 0
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
    variance: Optional[float] = None
    variance_reason: Optional[str] = None
    expenses: List[Expense] = []

    class Config:
        from_attributes = True

# Day Summary Schema
class DaySummary(BaseSchema):
    day_id: int
    closing_balance: float
    total_expense: float
    cash_in_hand: float
    cash_in_account: float
    message: Optional[str] = None
    opening_balance: float
    start_time: datetime
    end_time: Optional[datetime] = None
    variance: Optional[float] = None
    variance_reason: Optional[str] = None
    expenses: List[Expense] = []


class StatusResponse(BaseModel):
    day_started: bool
    active_day: Optional[Day] = None

class ShopStatusResponse(BaseModel):
    shop_id: int
    shop_name: str
    day_started: bool
    active_day: Optional[Day] = None