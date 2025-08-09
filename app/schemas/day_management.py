from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Expense Schemas
class ExpenseBase(BaseModel):
    description: str
    amount: float

class ExpenseCreate(ExpenseBase):
    day_id: int

class Expense(ExpenseBase):
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

class Day(DayBase):
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
class DaySummary(BaseModel):
    day_id: int
    closing_balance: float
    total_expense: float
    cash_in_hand: float
    cash_in_account: float
    message: str
