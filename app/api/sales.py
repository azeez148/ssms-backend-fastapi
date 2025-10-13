from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.sale import SaleCreate, SaleResponse
from app.services.sale import SaleService

router = APIRouter()
sale_service = SaleService()

@router.post("/addSale", response_model=SaleResponse)
async def add_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db)
):
    return sale_service.create_sale(db, sale)

@router.get("/all", response_model=List[SaleResponse])
async def get_all_sales(db: Session = Depends(get_db)):
    return sale_service.get_all_sales(db)

@router.get("/recent", response_model=List[SaleResponse])
async def get_recent_sales(db: Session = Depends(get_db)):
    return sale_service.get_recent_sales(db)

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
