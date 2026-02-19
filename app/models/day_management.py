from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel

class Day(BaseModel):
    __tablename__ = "days"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    opening_balance = Column(Float, nullable=False)
    closing_balance = Column(Float, nullable=True, default=0.0)
    total_expense = Column(Float, nullable=True, default=0.0)
    cash_in_hand = Column(Float, nullable=True, default=0.0)
    cash_in_account = Column(Float, nullable=True, default=0.0)
    variance = Column(Float, nullable=True, default=0.0)
    variance_reason = Column(String, nullable=True)

    expenses = relationship("Expense", back_populates="day")

class Expense(BaseModel):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    day_id = Column(Integer, ForeignKey("days.id"))
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    day = relationship("Day", back_populates="expenses")
