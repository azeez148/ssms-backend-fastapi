from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.stock import StockService
from app.schemas.stock import StockRequest, StockResponse, ClearStockRequest

router = APIRouter()

@router.post("/uploadExcel")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    stock_service = StockService()
    return await stock_service.upload_excel(db, file)

@router.post("/hold", response_model=StockResponse)
def hold_stock(stock_request: StockRequest, db: Session = Depends(get_db)):
    stock_service = StockService()
    return stock_service.hold_stock(db, stock_request)

@router.post("/release", response_model=StockResponse)
def release_stock(stock_request: StockRequest, db: Session = Depends(get_db)):
    stock_service = StockService()
    return stock_service.release_stock(db, stock_request)

@router.post("/check", response_model=StockResponse)
def check_stock(stock_request: StockRequest, db: Session = Depends(get_db)):
    stock_service = StockService()
    return stock_service.check_stock(db, stock_request)

