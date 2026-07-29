from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.pricelist import PricelistCreate, PricelistUpdate, PricelistResponse
from app.services.pricelist import PricelistService

router = APIRouter()
pricelist_service = PricelistService()

@router.post("/", response_model=PricelistResponse)
async def create_pricelist(
    pricelist: PricelistCreate,
    db: Session = Depends(get_db)
):
    # Check if a pricelist already exists for this category
    existing = pricelist_service.get_pricelist_by_category_id(db, pricelist.category_id)
    if existing:
        raise HTTPException(status_code=400, detail="Pricelist already exists for this category")
    return pricelist_service.create_pricelist(db, pricelist)

@router.get("/", response_model=List[PricelistResponse])
async def get_all_pricelists(db: Session = Depends(get_db)):
    return pricelist_service.get_all_pricelists(db)

@router.get("/{pricelist_id}", response_model=PricelistResponse)
async def get_pricelist(pricelist_id: int, db: Session = Depends(get_db)):
    pricelist = pricelist_service.get_pricelist_by_id(db, pricelist_id)
    if not pricelist:
        raise HTTPException(status_code=404, detail="Pricelist not found")
    return pricelist

@router.get("/category/{category_id}", response_model=PricelistResponse)
async def get_pricelist_by_category(category_id: int, db: Session = Depends(get_db)):
    pricelist = pricelist_service.get_pricelist_by_category_id(db, category_id)
    if not pricelist:
        raise HTTPException(status_code=404, detail="Pricelist not found for this category")
    return pricelist

@router.put("/{pricelist_id}", response_model=PricelistResponse)
async def update_pricelist(
    pricelist_id: int,
    pricelist: PricelistUpdate,
    db: Session = Depends(get_db)
):
    updated_pricelist = pricelist_service.update_pricelist(db, pricelist_id, pricelist)
    if not updated_pricelist:
        raise HTTPException(status_code=404, detail="Pricelist not found")
    return updated_pricelist

@router.delete("/{pricelist_id}")
async def delete_pricelist(pricelist_id: int, db: Session = Depends(get_db)):
    success = pricelist_service.delete_pricelist(db, pricelist_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pricelist not found")
    return {"message": "Pricelist deleted successfully"}
