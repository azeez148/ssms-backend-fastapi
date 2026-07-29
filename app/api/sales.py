from http.client import HTTPException
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.sale import SaleCreate, SaleResponse, SaleStatusUpdate, SaleListResponse
from app.services.sale import SaleService

router = APIRouter()
sale_service = SaleService()

@router.post("/addSale", response_model=SaleResponse)
async def add_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db)
):
    return sale_service.create_sale(db, sale)

@router.get("/all", response_model=SaleListResponse)
async def get_all_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    sales, total = sale_service.get_all_sales(db, skip=skip, limit=limit, status=status)
    return {
        "items": sales,
        "total": total,
        "page": (skip // limit) + 1,
        "per_page": limit
    }

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
    updated_sale = sale_service.update_sale(db, sale, sale_id)
    if not updated_sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return updated_sale

# get sale by id
@router.get("/{sale_id}", response_model=SaleResponse)
async def get_sale_by_id(sale_id: int, db: Session = Depends(get_db)):
    sale = sale_service.get_sale_by_id(db, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale
