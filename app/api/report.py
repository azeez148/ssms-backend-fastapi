from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, timedelta
from calendar import monthrange
from app.core.database import get_db
from app.schemas.report import SalesReportResponse, SalesComparisonResponse
from app.services.report import ReportService

router = APIRouter()
report_service = ReportService()

@router.get("/sales", response_model=SalesReportResponse)
async def get_sales_report(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    return report_service.get_sales_report(db, start_date, end_date)

@router.get("/sales/today", response_model=SalesReportResponse)
async def get_today_sales_report(db: Session = Depends(get_db)):
    today = date.today().isoformat()
    return report_service.get_sales_report(db, today, today)

@router.get("/sales/yesterday", response_model=SalesReportResponse)
async def get_yesterday_sales_report(db: Session = Depends(get_db)):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    return report_service.get_sales_report(db, yesterday, yesterday)

@router.get("/sales/this-week", response_model=SalesReportResponse)
async def get_this_week_sales_report(db: Session = Depends(get_db)):
    today = date.today()
    start_of_week = (today - timedelta(days=today.weekday())).isoformat()
    return report_service.get_sales_report(db, start_of_week, today.isoformat())

@router.get("/sales/last-week", response_model=SalesReportResponse)
async def get_last_week_sales_report(db: Session = Depends(get_db)):
    today = date.today()
    start_of_last_week = (today - timedelta(days=today.weekday() + 7)).isoformat()
    end_of_last_week = (today - timedelta(days=today.weekday() + 1)).isoformat()
    return report_service.get_sales_report(db, start_of_last_week, end_of_last_week)

@router.get("/sales/this-month", response_model=SalesReportResponse)
async def get_this_month_sales_report(db: Session = Depends(get_db)):
    today = date.today()
    start_of_month = today.replace(day=1).isoformat()
    return report_service.get_sales_report(db, start_of_month, today.isoformat())

@router.get("/sales/last-month", response_model=SalesReportResponse)
async def get_last_month_sales_report(db: Session = Depends(get_db)):
    today = date.today()
    first_of_current_month = today.replace(day=1)
    end_of_last_month = (first_of_current_month - timedelta(days=1)).isoformat()
    start_of_last_month = (first_of_current_month - timedelta(days=1)).replace(day=1).isoformat()
    return report_service.get_sales_report(db, start_of_last_month, end_of_last_month)

@router.get("/sales/this-year", response_model=SalesReportResponse)
async def get_this_year_sales_report(db: Session = Depends(get_db)):
    today = date.today()
    start_of_year = today.replace(month=1, day=1).isoformat()
    return report_service.get_sales_report(db, start_of_year, today.isoformat())

@router.get("/sales/compare", response_model=SalesComparisonResponse)
async def compare_sales_reports(
    period: str = Query(..., description="Period type: 'day', 'week', 'month', or 'year'"),
    period_1_start: str = Query(..., description="Start date of period 1 in YYYY-MM-DD format"),
    period_2_start: str = Query(..., description="Start date of period 2 in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Compare sales between two periods.
    - **day**: compares the single day of each period_start
    - **week**: compares 7 days starting from each period_start (Mon-Sun)
    - **month**: compares the full month of each period_start date
    - **year**: compares the full year of each period_start date
    """
    try:
        p1_start = date.fromisoformat(period_1_start)
        p2_start = date.fromisoformat(period_2_start)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    period = period.lower()
    if period not in ("day", "week", "month", "year"):
        raise HTTPException(status_code=400, detail="Period must be 'day', 'week', 'month', or 'year'.")

    def resolve_range(start: date, period_type: str):
        if period_type == "day":
            return start, start
        elif period_type == "week":
            week_start = start - timedelta(days=start.weekday())
            week_end = week_start + timedelta(days=6)
            return week_start, week_end
        elif period_type == "month":
            month_start = start.replace(day=1)
            last_day = monthrange(start.year, start.month)[1]
            month_end = start.replace(day=last_day)
            return month_start, month_end
        elif period_type == "year":
            year_start = start.replace(month=1, day=1)
            year_end = start.replace(month=12, day=31)
            return year_start, year_end

    p1_start_resolved, p1_end = resolve_range(p1_start, period)
    p2_start_resolved, p2_end = resolve_range(p2_start, period)

    return report_service.compare_sales_reports(
        db,
        p1_start_resolved.isoformat(), p1_end.isoformat(),
        p2_start_resolved.isoformat(), p2_end.isoformat(),
        period
    )

