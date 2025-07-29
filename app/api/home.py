from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from pathlib import Path
from fastapi.responses import FileResponse

from app.core.database import get_db
from app.schemas.home import HomeResponse
from app.services.home import HomeService

router = APIRouter()
home_service = HomeService()

@router.get("/all", response_model=HomeResponse)
async def get_home_data(db: Session = Depends(get_db)):
    return home_service.get_home_data(db)

@router.get("/{product_id}/image")
async def get_product_image(product_id: int):
    image_dir = Path("images/products") / str(product_id)
    
    if not image_dir.exists():
        # Return default image
        return FileResponse("images/notfound.png")
    
    # Return the first image found for the product
    try:
        image_file = next(image_dir.glob("*"))
        return FileResponse(str(image_file))
    except StopIteration:
        return FileResponse("images/notfound.png")
