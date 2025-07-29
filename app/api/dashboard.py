from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from typing import Dict
from app.services.dashboard import DashboardService

router = APIRouter()
dashboard_service = DashboardService()

@router.get("/all", response_model=Dict)
async def get_dashboard_data(db: Session = Depends(get_db)):
    return dashboard_service.get_dashboard_data(db)
