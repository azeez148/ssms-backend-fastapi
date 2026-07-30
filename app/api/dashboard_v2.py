from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.dashboard_v2 import DashboardV2Response
from app.services.dashboard_v2 import DashboardV2Service

router = APIRouter()
_service = DashboardV2Service()


@router.get("", response_model=DashboardV2Response)
async def get_v2_dashboard(
    view: Literal["daily", "monthly", "yearly"] = Query(default="daily", description="Time period view"),
    db: Session = Depends(get_db),
):
    return _service.get_dashboard_data(db, view)
