from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.base import BaseSchema

# Expense Schemas
class ExpenseBase(BaseModel):
    description: str
    amount: float

class ExpenseCreate(ExpenseBase):
    day_id: int

class Expense(ExpenseBase, BaseSchema):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# Day Schemas
class DayBase(BaseModel):
    opening_balance: float

class DayCreate(DayBase):
    pass

class DayUpdate(BaseModel):
    closing_balance: float
    total_expense: float
    cash_in_hand: float
    cash_in_account: float
    end_time: datetime

class Day(DayBase, BaseSchema):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    closing_balance: Optional[float] = None
    total_expense: Optional[float] = None
    cash_in_hand: Optional[float] = None
    cash_in_account: Optional[float] = None
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
    message: str
    opening_balance: float
    start_time: datetime
    end_time: Optional[datetime] = None
    expenses: List[Expense] = []


class StatusResponse(BaseModel):
    day_started: bool
    active_day: Optional[Day] = None