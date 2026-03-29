from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, cast, Date
from datetime import datetime, date
from typing import List, Optional

from app.models.day_management import Day, Expense
from app.models.sale import Sale
from app.models.payment import PaymentType
from app.schemas.enums import SaleStatus
from app.schemas.day_management import DayCreate, ExpenseCreate, DaySummary
from app.services.notification import EmailNotificationService
from app.core.config import settings
from app.core.logging import logger

class DayManagementService:
    def __init__(self):
        self.email_notification_service = EmailNotificationService()

    def get_active_day(self, db: Session, shop_id: int) -> Optional[Day]:
        """
        Retrieves the currently active day for a specific shop (a day that has been started but not ended).
        """
        return db.query(Day).filter(Day.shop_id == shop_id, Day.end_time.is_(None)).first()

    def start_day(self, db: Session, day: DayCreate) -> Day:
        """
        Starts a new day or reopens an existing one for the current date for a specific shop.
        - If a day is already active for today in this shop, it returns the active day.
        - If a day was started and ended today in this shop, it reopens that day.
        - If no day has been started today in this shop, it creates a new one.
        """
        today = datetime.utcnow().date()
        shop_id = day.shop_id or 1

        # Query for a day that was started today for this shop
        day_for_today = db.query(Day).filter(
            Day.shop_id == shop_id,
            cast(Day.start_time, Date) == today
        ).first()

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
            active_day = self.get_active_day(db, shop_id)
            if active_day:
                raise Exception(f"An active day already exists for shop {shop_id} from a previous date. Please end it before starting a new one.")

            db_day = Day(
                shop_id=shop_id,
                opening_balance=day.opening_balance,
                cash_in_hand=day.opening_balance,
                cash_in_account=0.0,
                total_expense=0.0,
                created_by="system",
                updated_by="system"
            )
            db.add(db_day)
            db.commit()
            db.refresh(db_day)

            try:
                self.email_notification_service.send_day_start_notification(db_day)
            except Exception as e:
                logger.error(f"Failed to send day start notification: {str(e)}")

            return db_day

    def add_expense(self, db: Session, expense: ExpenseCreate, shop_id: Optional[int] = None) -> Expense:
        """
        Adds a new expense to the currently active day for a specific shop.
        If no day is active, it raises an exception.
        """
        # If shop_id is not provided, we try to get the day from the expense itself if it has day_id
        # But usually we want to ensure it's the active day for the shop.
        if shop_id:
            active_day = self.get_active_day(db, shop_id)
        else:
            # Fallback to day_id if shop_id not provided (might be needed for some backward compatibility or internal calls)
            active_day = db.query(Day).filter(Day.id == expense.day_id, Day.end_time.is_(None)).first()

        if not active_day:
            raise Exception("No active day found for this shop. Please start a day before adding expenses.")

        db_expense = Expense(
            day_id=active_day.id,
            description=expense.description,
            amount=expense.amount,
            created_by="system",
            updated_by="system"
        )
        db.add(db_expense)

        # Update active day totals
        active_day.total_expense = (active_day.total_expense or 0.0) + expense.amount
        active_day.cash_in_hand = (active_day.cash_in_hand or 0.0) - expense.amount
        active_day.updated_by = "system"

        db.commit()
        db.refresh(db_expense)

        try:
            self.email_notification_service.send_expense_added_notification(db_expense)
        except Exception as e:
            logger.error(f"Failed to send expense notification: {str(e)}")

        return db_expense

    def update_day_from_sale(self, db: Session, amount_change: float, payment_type_id: int, shop_id: int):
        """
        Updates the active day's cash or account balance based on a sale change for a specific shop.
        """
        active_day = self.get_active_day(db, shop_id)
        if not active_day:
            return

        payment_type = db.query(PaymentType).filter(PaymentType.id == payment_type_id).first()
        if not payment_type:
            return

        if payment_type.name == 'Cash on Delivery':
            active_day.cash_in_hand = (active_day.cash_in_hand or 0.0) + amount_change
        else:
            active_day.cash_in_account = (active_day.cash_in_account or 0.0) + amount_change

        active_day.updated_by = "system"

    def get_expenses_for_day(self, db: Session, day_id: int) -> List[Expense]:
        """
        Retrieves all expenses for a specific day.
        """
        return db.query(Expense).filter(Expense.day_id == day_id).all()

    def end_day(self, db: Session, day_id: int, closing_balance_actual: float = None, variance: float = 0, variance_reason: str = None) -> Day:
        """
        Ends the specified day, calculates totals, and updates the day's record.
        """
        db_day = db.query(Day).filter(Day.id == day_id).first()
        if not db_day:
            raise Exception("Day not found.")

        if db_day.end_time is not None:
            raise Exception("This day has already been ended.")

        # Final recalculation to ensure accuracy
        total_expense = db.query(func.sum(Expense.amount)).filter(Expense.day_id == day_id).scalar() or 0.0

        target_date = db_day.start_time.date().isoformat()
        sales_for_day = db.query(Sale).options(joinedload(Sale.payment_type)).filter(
            Sale.date == target_date,
            Sale.status != SaleStatus.CANCELLED,
            Sale.shop_id == db_day.shop_id
        ).all()

        total_cash_sales = sum(sale.total_price for sale in sales_for_day if sale.payment_type.name == 'Cash on Delivery')
        total_account_sales = sum(sale.total_price for sale in sales_for_day if sale.payment_type.name != 'Cash on Delivery')

        # Update day record
        db_day.end_time = datetime.now()
        db_day.total_expense = total_expense
        db_day.cash_in_hand = db_day.opening_balance + total_cash_sales - total_expense
        db_day.cash_in_account = total_account_sales
        db_day.closing_balance = db_day.cash_in_hand + db_day.cash_in_account
        
        # Set variance (default to 0 if not provided)
        db_day.variance = variance if variance is not None else 0
        # Set variance_reason (default to None if not provided)
        db_day.variance_reason = variance_reason

        db_day.updated_by = "system"
        db.commit()
        db.refresh(db_day)

        # Send notifications
        try:
            day_summary = self.get_day_summary(db, day_id)
            self.email_notification_service.send_day_summary_notification(day_summary)
        except Exception as e:
            logger.error(f"Failed to send day summary notification: {str(e)}")

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
            closing_balance=db_day.closing_balance or 0.0,
            total_expense=db_day.total_expense or 0.0,
            cash_in_hand=db_day.cash_in_hand or 0.0,
            cash_in_account=db_day.cash_in_account or 0.0,
            opening_balance=db_day.opening_balance,
            start_time=db_day.start_time,
            end_time=db_day.end_time,
            variance=db_day.variance or 0.0,
            variance_reason=db_day.variance_reason,
            expenses=self.get_expenses_for_day(db, day_id),
            message="Day summary retrieved successfully."
        )

    def get_all_shops_status(self, db: Session) -> List[dict]:
        """
        Retrieves the status of all shops (whether they have an active day).
        """
        from app.models.shop import Shop
        shops = db.query(Shop).all()
        status_list = []
        for shop in shops:
            active_day = self.get_active_day(db, shop.id)
            status_list.append({
                "shop_id": shop.id,
                "shop_name": shop.name,
                "day_started": active_day is not None,
                "active_day": active_day
            })
        return status_list
