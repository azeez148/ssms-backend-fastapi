from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from httpcore import request
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
import pandas as pd
from pathlib import Path
import tempfile

from app.core.database import get_db
from app.models.category_discount import CategoryDiscount
from app.schemas.product import (
    CategoryDiscountUpdateRequest,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    UpdateSizeMapRequest,
    ProductFilterRequest,
    CategoryDiscountRequest,
    CategoryDiscountResponse
)
from app.schemas.category import CategoryBase
from app.core.logging import logger
from app.schemas.stock import ClearStockRequest, StockResponse
from app.services.product import ProductService
from app.services.category import CategoryService
from app.services.stock import StockService

router = APIRouter()
product_service = ProductService()
category_service = CategoryService()

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
        logger.error(f"Product with id {product_update.id} not found")
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.post("/updateSizeMap", response_model=ProductResponse)
async def update_size_map(
    update_request: UpdateSizeMapRequest,
    db: Session = Depends(get_db)
):
    updated_product = product_service.update_size_map(db, update_request)
    if not updated_product:
        logger.error(f"Product with id {update_request.product_id} not found")
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.post("/import-excel", response_model=List[ProductResponse])
async def import_products_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.xlsx'):
        logger.error(f"Invalid file format for {file.filename}")
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
            
            # Fetch category
            category_id = int(row['category_id'])
            category_model = category_service.get_category_by_id(db, category_id)
            if not category_model:
                logger.error(f"Category with id {category_id} not found")
                raise HTTPException(status_code=400, detail=f"Category with id {category_id} not found")

            category_schema = CategoryBase.from_orm(category_model)

            # Create product data
            product_data = ProductCreate(
                name=row['name'],
                description=row['description'],
                unit_price=int(row['unit_price']),
                selling_price=int(row['selling_price']),
                category_id=category_id,
                is_active=bool(row['is_active']),
                can_listed=bool(row['can_listed']),
                size_map=size_map,
                category=category_schema
            )
            
            # Create product in database
            product = product_service.create_product(db, product_data)
            products.append(product)
        
        return products
        
    except Exception as e:
        logger.exception(f"Error importing products from excel: {e}")
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

@router.post("/upload-images", response_model=ProductResponse)
async def upload_product_images(
    product_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Define the directory to store the image
    upload_dir = Path(f"images/products/{product_id}")
    os.makedirs(upload_dir, exist_ok=True)

    # Delete any existing files in the directory
    for existing_file in upload_dir.iterdir():
        if existing_file.is_file():
            existing_file.unlink()

    # Rename the uploaded file to product_id with its original extension
    file_ext = Path(image.filename).suffix
    new_filename = f"{product_id}{file_ext}"
    file_path = upload_dir / new_filename

    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Update the product's image_url in the database
    image_url = str(file_path).replace("\\", "/")
    updated_product = product_service.update_product_image_url(db, product_id, image_url)

    if not updated_product:
        logger.error(f"Product with id {product_id} not found")
        raise HTTPException(status_code=404, detail="Product not found")

    return updated_product

@router.post("/addDefaultCategoryDiscounts", response_model=List[CategoryDiscountResponse])
async def add_default_category_discounts(
    request: CategoryDiscountRequest,
    db: Session = Depends(get_db)
):
    return product_service.add_default_category_discounts(db, request)


@router.get("/categoryDiscounts/{category_id}", response_model=List[CategoryDiscountResponse])
async def get_category_discount_for_category(
    category_id: int,
    db: Session = Depends(get_db)
) -> List[CategoryDiscountResponse]:
    return product_service.get_category_discounts(db, category_id)


@router.get("/getDefaultCategoryDiscounts", response_model=List[CategoryDiscountResponse])
async def get_default_category_discounts(
    db: Session = Depends(get_db)
) -> List[CategoryDiscountResponse]:
    return product_service.get_default_category_discounts(db)

@router.post("/updateCategoryDiscount", response_model=List[CategoryDiscountResponse])
async def update_category_discount_for_category(
    request: CategoryDiscountUpdateRequest,
    db: Session = Depends(get_db)
) -> List[CategoryDiscountResponse]:
    return product_service.update_category_discount(db, request)

# add api to delete category discount for category
@router.delete("/deleteDefaultCategoryDiscount/{id}", response_model=CategoryDiscountResponse)
async def delete_default_category_discount(
    id: int,
    db: Session = Depends(get_db)
):
    db_discount = db.query(CategoryDiscount).filter(CategoryDiscount.id == id).first()
    if not db_discount:
        logger.error(f"Category discount with id {id} not found")
        raise HTTPException(status_code=404, detail="Category discount not found")

    db.delete(db_discount)
    db.commit()
    return db_discount


@router.post("/clearStock", response_model=StockResponse)
def clear_stock(clear_request: ClearStockRequest, db: Session = Depends(get_db)):
    stock_service = StockService()
    return stock_service.clear_stock(db, clear_request)