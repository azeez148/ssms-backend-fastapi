from fastapi import APIRouter, Depends
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
