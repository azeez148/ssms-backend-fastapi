from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.stock import StockService

router = APIRouter()

@router.post("/uploadExcel")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    stock_service = StockService()
    return await stock_service.upload_excel(db, file)
