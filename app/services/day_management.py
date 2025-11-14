from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, cast, Date
from datetime import datetime, date
from typing import List, Optional

from app.models.day_management import Day, Expense
from app.models.sale import Sale
from app.models.payment import PaymentType
from app.schemas.day_management import DayCreate, ExpenseCreate, DaySummary
from app.services.notification import EmailNotificationService, WhatsAppNotificationService
from app.core.config import settings

class DayManagementService:
    def __init__(self):
        self.email_notification_service = EmailNotificationService()
        self.whatsapp_notification_service = WhatsAppNotificationService()

    def get_active_day(self, db: Session) -> Optional[Day]:
        """
        Retrieves the currently active day (a day that has been started but not ended).
        """
        return db.query(Day).filter(Day.end_time.is_(None)).first()

    def start_day(self, db: Session, day: DayCreate) -> Day:
        """
        Starts a new day or reopens an existing one for the current date.
        - If a day is already active for today, it returns the active day.
        - If a day was started and ended today, it reopens that day.
        - If no day has been started today, it creates a new one.
        """
        today = datetime.utcnow().date()

        # Query for a day that was started today
        day_for_today = db.query(Day).filter(cast(Day.start_time, Date) == today).first()

        if day_for_today:
            if day_for_today.end_time is None:
                # Day is already active, just return it
                return day_for_today
            else:
                # Day was ended, reopen it
                day_for_today.end_time = None
                day_for_today.updated_by = "system"
                db.commit()
                db.refresh(day_for_today)
                return day_for_today
        else:
            # No day started today, create a new one
            active_day = self.get_active_day(db)
            if active_day:
                raise Exception("An active day already exists from a previous date. Please end it before starting a new one.")

            db_day = Day(opening_balance=day.opening_balance, created_by="system", updated_by="system")
            db.add(db_day)
            db.commit()
            db.refresh(db_day)
            return db_day

    def add_expense(self, db: Session, expense: ExpenseCreate) -> Expense:
        """
        Adds a new expense to the currently active day.
        If no day is active, it raises an exception.
        """
        active_day = self.get_active_day(db)
        if not active_day:
            raise Exception("No active day found. Please start a day before adding expenses.")

        db_expense = Expense(
            day_id=active_day.id,
            description=expense.description,
            amount=expense.amount,
            created_by="system",
            updated_by="system"
        )
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
        return db_expense

    def get_expenses_for_day(self, db: Session, day_id: int) -> List[Expense]:
        """
        Retrieves all expenses for a specific day.
        """
        return db.query(Expense).filter(Expense.day_id == day_id).all()

    def end_day(self, db: Session, day_id: int) -> Day:
        """
        Ends the specified day, calculates totals, and updates the day's record.
        """
        db_day = db.query(Day).filter(Day.id == day_id).first()
        if not db_day:
            raise Exception("Day not found.")

        if db_day.end_time is not None:
            raise Exception("This day has already been ended.")

        # Calculate total expenses for the day
        total_expense = db.query(func.sum(Expense.amount)).filter(Expense.day_id == day_id).scalar() or 0.0

        # Calculate total sales for the day
        end_time = datetime.now()
        start_time_str = db_day.start_time.isoformat()
        end_time_str = end_time.isoformat()

        target_date = db_day.start_time.date().isoformat()

        sales_for_day = db.query(Sale).options(joinedload(Sale.payment_type)).filter(
            Sale.date == target_date
        ).all()

        total_sales = sum(sale.total_price for sale in sales_for_day)

        cash_in_hand = sum(sale.total_price for sale in sales_for_day if sale.payment_type.name == 'Cash on Delivery')
        cash_in_account = sum(sale.total_price for sale in sales_for_day if sale.payment_type.name != 'Cash on Delivery')


        # Calculate closing balance
        closing_balance = (db_day.opening_balance + total_sales) - total_expense

        # Update day record
        db_day.end_time = end_time
        db_day.total_expense = total_expense
        db_day.closing_balance = closing_balance
        db_day.cash_in_hand = cash_in_hand
        db_day.cash_in_account = cash_in_account

        db_day.updated_by = "system"
        db.commit()
        db.refresh(db_day)

        # Send notifications
        day_summary = self.get_day_summary(db, day_id)
        self.email_notification_service.send_day_summary_notification(day_summary)
        self.whatsapp_notification_service.send_day_summary_notification(day_summary, settings.ADMIN_PHONE_NUMBER)

        return db_day

    def get_day_summary(self, db: Session, day_id: int) -> DaySummary:
        """
        Generates a summary for a specific day.
        """
        db_day = db.query(Day).filter(Day.id == day_id).first()
        if not db_day:
            raise Exception("Day not found.")

        return DaySummary(
            day_id=db_day.id,
            closing_balance=db_day.closing_balance,
            total_expense=db_day.total_expense,
            cash_in_hand=db_day.cash_in_hand,
            cash_in_account=db_day.cash_in_account,
            opening_balance=db_day.opening_balance,
            start_time=db_day.start_time,
            end_time=db_day.end_time,
            expenses=self.get_expenses_for_day(db, day_id),
            message="Day ended successfully."
        )
