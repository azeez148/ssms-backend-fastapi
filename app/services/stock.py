import openpyxl
import json
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.services.product import ProductService
from app.services.category import CategoryService
from app.schemas.product import ProductCreate, ProductSizeCreate

class StockService:
    def __init__(self):
        self.product_service = ProductService()
        self.category_service = CategoryService()

    async def upload_excel(self, db: Session, file: UploadFile):
        if not file.filename.endswith('.xlsx'):
            raise HTTPException(status_code=400, detail="Invalid file format. Please upload an Excel file.")

        try:
            workbook = openpyxl.load_workbook(file.file)
            sheet = workbook.active
            is_header = True
            for row in sheet.iter_rows(values_only=True):
                if is_header:
                    is_header = False
                    continue

                name, description, category_name, size_map_str, unit_price, selling_price = row

                # Parse the size map string
                try:
                    size_map_json = json.loads(size_map_str.replace("'", "\""))
                    size_map = [ProductSizeCreate(size=k, quantity=v) for k, v in size_map_json.items()]
                except json.JSONDecodeError:
                    raise HTTPException(status_code=400, detail=f"Invalid size_map format for product {name}")

                # Find the category
                category = self.category_service.find_category_by_name(db, category_name)
                if not category:
                    raise HTTPException(status_code=404, detail=f"Category '{category_name}' not found for product {name}")

                product_data = ProductCreate(
                    name=name,
                    description=description,
                    category_id=category.id,
                    size_map=size_map,
                    unit_price=unit_price,
                    selling_price=selling_price,
                    is_active=True,
                    can_listed=True
                )
                self.product_service.create_product(db, product_data)

            return {"message": "Excel uploaded and processed successfully."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not upload/process the file: {e}")
