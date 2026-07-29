from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.services.dashboard import DashboardService
from app.schemas.dashboard import Dashboard

router = APIRouter()
dashboard_service = DashboardService()

@router.get("/all", response_model=Dashboard)
async def get_dashboard_data(
    shop_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    return dashboard_service.get_dashboard_data(db, shop_id=shop_id)
