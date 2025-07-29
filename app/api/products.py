from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
import pandas as pd
from pathlib import Path
import tempfile

from app.core.database import get_db
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    UpdateSizeMapRequest,
    ProductFilterRequest
)
from app.services.product import ProductService

router = APIRouter()
product_service = ProductService()

@router.post("/addProduct", response_model=ProductResponse)
async def add_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    return product_service.create_product(db, product)

@router.get("/all", response_model=List[ProductResponse])
async def get_all_products(db: Session = Depends(get_db)):
    return product_service.get_all_products(db)

@router.post("/updateProduct", response_model=ProductResponse)
async def update_product(
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    updated_product = product_service.update_product(db, product_update)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.post("/updateSizeMap", response_model=ProductResponse)
async def update_size_map(
    update_request: UpdateSizeMapRequest,
    db: Session = Depends(get_db)
):
    updated_product = product_service.update_size_map(db, update_request)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.post("/import-excel", response_model=List[ProductResponse])
async def import_products_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Only Excel (.xlsx) files are allowed")
    
    # Create a temporary file to store the upload
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name
    
    try:
        # Read the Excel file
        df = pd.read_excel(temp_path)
        
        products = []
        for _, row in df.iterrows():
            # Create size map from size columns
            size_map = []
            for size in ['S', 'M', 'L', 'XL', 'XXL']:
                quantity = row.get(f'size_{size}', 0)
                if quantity > 0:
                    size_map.append({"size": size, "quantity": int(quantity)})
            
            # Create product data
            product_data = ProductCreate(
                name=row['name'],
                description=row['description'],
                unit_price=int(row['unit_price']),
                selling_price=int(row['selling_price']),
                category_id=int(row['category_id']),
                is_active=bool(row['is_active']),
                can_listed=bool(row['can_listed']),
                size_map=size_map
            )
            
            # Create product in database
            product = product_service.create_product(db, product_data)
            products.append(product)
        
        return products
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        # Clean up the temporary file
        os.unlink(temp_path)

@router.post("/filterProducts", response_model=List[ProductResponse])
async def get_filtered_products(
    filter_request: ProductFilterRequest,
    db: Session = Depends(get_db)
):
    return product_service.get_filtered_products(
        db,
        filter_request.category_id,
        filter_request.product_type_filter
    )

@router.post("/upload-images")
async def upload_product_images(
    product_id: int,
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    upload_dir = Path("images/products") / str(product_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    saved_files = []
    for image in images:
        file_path = upload_dir / image.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        saved_files.append(str(file_path))
    
    return {"message": "Images uploaded successfully", "files": saved_files}
