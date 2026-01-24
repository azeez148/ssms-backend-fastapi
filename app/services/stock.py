import openpyxl
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.services.product import ProductService
from app.services.category import CategoryService
from app.schemas.product import ProductCreate, ProductSizeCreate
from app.schemas.stock import StockRequest, StockResponse
from app.models.product_size import ProductSize

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

            headers = [cell.value for cell in sheet[1]]

            for row_index in range(2, sheet.max_row + 1):
                row_values = [cell.value for cell in sheet[row_index]]
                row_data = dict(zip(headers, row_values))

                name = row_data.get('name')
                description = row_data.get('description')
                category_id = row_data.get('category_id')
                unit_price = row_data.get('unit_price')
                selling_price = row_data.get('selling_price')
                is_active = row_data.get('is_active', True)
                can_listed = row_data.get('can_listed', True)

                if not all([name, category_id, unit_price, selling_price]):
                    raise HTTPException(status_code=400, detail=f"Missing required data in row {row_index}")

                # Find the category
                category = self.category_service.get_category_by_id(db, category_id)
                if not category:
                    raise HTTPException(status_code=404, detail=f"Category with id '{category_id}' not found for product {name}")

                size_map = []
                for key, value in row_data.items():
                    if key.startswith('size_') and value is not None and int(value) > 0:
                        size = key.split('_')[1]
                        quantity = int(value)
                        size_map.append(ProductSizeCreate(size=size, quantity=quantity))

                product_data = ProductCreate(
                    name=name,
                    description=description,
                    category_id=category.id,
                    size_map=size_map,
                    unit_price=unit_price,
                    selling_price=selling_price,
                    is_active=bool(is_active),
                    can_listed=bool(can_listed),
                    category=category
                )
                self.product_service.create_product(db, product_data)

            return {"message": "Excel uploaded and processed successfully."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not upload/process the file: {str(e)}")

    def hold_stock(self, db: Session, stock_request: StockRequest) -> StockResponse:
        try:
            for item in stock_request.items:
                self.product_service.update_product_stock(db, item.product_id, item.size, -item.quantity, stock_request.shop_id)
            return StockResponse(success=True, message="Stock held successfully.")
        except HTTPException as e:
            return StockResponse(success=False, message=e.detail)
        except Exception as e:
            return StockResponse(success=False, message=str(e))

    def release_stock(self, db: Session, stock_request: StockRequest) -> StockResponse:
        try:
            for item in stock_request.items:
                self.product_service.update_product_stock(db, item.product_id, item.size, item.quantity, stock_request.shop_id)
            return StockResponse(success=True, message="Stock released successfully.")
        except HTTPException as e:
            return StockResponse(success=False, message=e.detail)
        except Exception as e:
            return StockResponse(success=False, message=str(e))

    def check_stock(self, db: Session, stock_request: StockRequest) -> StockResponse:
        try:
            for item in stock_request.items:
                product_size = db.query(ProductSize).filter(
                    ProductSize.product_id == item.product_id,
                    ProductSize.size == item.size,
                    ProductSize.shop_id == stock_request.shop_id
                ).first()

                if not product_size or product_size.quantity < item.quantity:
                    product = self.product_service.get_product_by_id(db, item.product_id)
                    product_name = product.name if product else "Unknown"
                    size_name = item.size
                    available_stock = product_size.quantity if product_size else 0

                    return StockResponse(
                        success=False,
                        message=f"Insufficient stock for {product_name} (Size: {size_name}). Available: {available_stock}, Requested: {item.quantity}"
                    )
            return StockResponse(success=True, message="Stock is available.")
        except Exception as e:
            return StockResponse(success=False, message=str(e))
