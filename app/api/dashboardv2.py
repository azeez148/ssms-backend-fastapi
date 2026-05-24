from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.dashboardv2 import DashboardV2Response
from app.services.dashboardv2 import DashboardV2Service

router = APIRouter()
dashboardv2_service = DashboardV2Service()


@router.get("/performance", response_model=DashboardV2Response)
async def get_dashboardv2_performance(
    period: str = Query(
        "daily",
        description="Supported values: daily, weekly, monthly, yearly, custom",
    ),
    date_value: Optional[str] = Query(
        None,
        alias="date",
        description="Anchor date (YYYY-MM-DD) for daily/weekly/monthly/yearly periods",
    ),
    start_date: Optional[str] = Query(
        None,
        description="Start date in YYYY-MM-DD format. Required when period=custom.",
    ),
    end_date: Optional[str] = Query(
        None,
        description="End date in YYYY-MM-DD format. Required when period=custom.",
    ),
    shop_id: Optional[int] = Query(
        None,
        description="Optional shop id. Omit to return all-shops aggregate.",
    ),
    db: Session = Depends(get_db),
):
    try:
        return dashboardv2_service.get_dashboard_performance(
            db=db,
            period=period,
            shop_id=shop_id,
            anchor_date=date_value,
            start_date=start_date,
            end_date=end_date,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
