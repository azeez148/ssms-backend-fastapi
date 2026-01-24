from http.client import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.sale import SaleCreate, SaleResponse, SaleStatusUpdate
from app.services.sale import SaleService
from app.api.auth import get_current_active_user
from app.models.user import User

router = APIRouter()
sale_service = SaleService()

@router.post("/addSale", response_model=SaleResponse)
async def add_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from app.schemas.enums import UserRole
    if current_user.role != UserRole.ADMINISTRATOR:
        if sale.shop_id not in [s.id for s in current_user.shops]:
            raise HTTPException(status_code=403, detail="You do not have access to this shop")
    return sale_service.create_sale(db, sale)

@router.get("/all", response_model=List[SaleResponse])
async def get_all_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return sale_service.get_all_sales(db, current_user)

@router.get("/recent", response_model=List[SaleResponse])
async def get_recent_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return sale_service.get_recent_sales(db, current_user)

@router.get("/most-sold")
async def get_most_sold_items(db: Session = Depends(get_db)):
    return sale_service.get_most_sold_items(db)

@router.get("/total")
async def get_total_sales(db: Session = Depends(get_db)):
    return {"total_sales": sale_service.get_total_sales(db)}

@router.put("/{sale_id}/complete", response_model=SaleResponse)
async def complete_sale(sale_id: int, db: Session = Depends(get_db)):
    return sale_service.update_sale_status(db, sale_id, "COMPLETED")

@router.put("/{sale_id}/cancel", response_model=SaleResponse)
async def cancel_sale(sale_id: int, db: Session = Depends(get_db)):
    return sale_service.cancel_sale(db, sale_id)

@router.put("/{sale_id}/updateStatus", response_model=SaleResponse)
async def update_sale_status_background(
    sale_id: int,
    status: SaleStatusUpdate,
    db: Session = Depends(get_db)  # ✅ Proper dependency injection
):
    sale = sale_service.update_sale_status(db, sale_id, status.status)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale  # ✅ Must return ORM or Pydantic object

@router.post("/{sale_id}/updateSale", response_model=SaleResponse)
async def update_sale(sale_id: int, sale: SaleCreate, db: Session = Depends(get_db)):
    return sale_service.update_sale(db, sale, sale_id)
