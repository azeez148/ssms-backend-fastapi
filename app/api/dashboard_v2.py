from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.services.dashboard_v2 import DashboardV2Service
from app.schemas.dashboard_v2 import DashboardV2Response

router = APIRouter()
dashboard_service = DashboardV2Service()

@router.get("", response_model=DashboardV2Response)
async def get_dashboard_v2_data(
    shop_id: Optional[int] = Query(None, description="Filter by shop ID"),
    start_date: Optional[str] = Query(None, description="Custom start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Custom end date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard data including performance, stock insights, and financials.
    Supports filtering by shop and custom date range for performance metrics.
    """
    return dashboard_service.get_dashboard_data(
        db,
        shop_id=shop_id,
        start_date=start_date,
        end_date=end_date
    )
