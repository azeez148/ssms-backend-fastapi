from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.schemas.report import SalesReportResponse
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
