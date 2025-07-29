from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException

from app.models.product import Product
from app.models.product_size import ProductSize
from app.schemas.product import ProductCreate, ProductUpdate, UpdateSizeMapRequest

class ProductService:
    def create_product(self, db: Session, product: ProductCreate) -> Product:
        db_product = Product(
            name=product.name,
            description=product.description,
            unit_price=product.unit_price,
            selling_price=product.selling_price,
            category_id=product.category_id,
            is_active=product.is_active,
            can_listed=product.can_listed
        )
        
        # Handle size_map separately
        if product.size_map:
            for size_data in product.size_map:
                size = ProductSize(
                    size=size_data.size,
                    quantity=size_data.quantity
                )
                db_product.size_map.append(size)
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product

    def get_all_products(self, db: Session) -> List[Product]:
        return db.query(Product).all()

    def get_product_by_id(self, db: Session, product_id: int) -> Optional[Product]:
        return db.query(Product).filter(Product.id == product_id).first()

    def update_product(self, db: Session, product_update: ProductUpdate) -> Optional[Product]:
        db_product = self.get_product_by_id(db, product_update.id)
        if not db_product:
            return None
            
        for field, value in product_update.dict().items():
            setattr(db_product, field, value)
            
        db.commit()
        db.refresh(db_product)
        return db_product

    def update_size_map(self, db: Session, update_request: UpdateSizeMapRequest) -> Optional[Product]:
        db_product = self.get_product_by_id(db, update_request.product_id)
        if not db_product:
            return None
            
        # Clear existing sizes
        db_product.size_map.clear()
        
        # Add new sizes
        for size, quantity in update_request.size_map.items():
            size_obj = ProductSize(
                size=size,
                quantity=quantity
            )
            db_product.size_map.append(size_obj)
            
        db.commit()
        db.refresh(db_product)
        return db_product

    def get_filtered_products(
        self,
        db: Session,
        category_id: Optional[int] = None,
        product_type_filter: Optional[str] = None
    ) -> List[Product]:
        query = db.query(Product)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
            
        if product_type_filter:
            # Add any specific filtering logic based on product type
            pass
            
        return query.all()
