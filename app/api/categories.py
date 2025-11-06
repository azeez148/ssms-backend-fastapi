from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.category import CategoryCreate, CategoryResponse
from app.services.category import CategoryService

router = APIRouter()
category_service = CategoryService()

@router.post("/addCategory", response_model=CategoryResponse)
async def add_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    return category_service.create_category(db, category)

@router.get("/all", response_model=List[CategoryResponse])
async def get_all_categories(db: Session = Depends(get_db)):
    return category_service.get_all_categories(db)

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    category = category_service.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    updated_category = category_service.update_category(db, category_id, category)
    if not updated_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated_category