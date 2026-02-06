import os
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException

from app.core.logging import logger
from app.models.product import Product
from app.models.product_size import ProductSize
from app.models.category_discount import CategoryDiscount
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    UpdateSizeMapRequest,
    CategoryDiscountRequest
)

class ProductService:
    def create_product(self, db: Session, product: ProductCreate) -> Product:
        db_product = Product(
            name=product.name,
            description=product.description,
            unit_price=product.unit_price,
            selling_price=product.selling_price,
            discounted_price=product.discounted_price,
            category_id=product.category_id,
            is_active=product.is_active,
            can_listed=product.can_listed,
            created_by="system",
            updated_by="system"
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
        products = db.query(Product).all()
        return products

    def get_product_by_id(self, db: Session, product_id: int) -> Optional[Product]:
        product = db.query(Product).filter(Product.id == product_id).first()
        return product

    def update_product(self, db: Session, product_update: ProductUpdate) -> Optional[Product]:
        db_product = self.get_product_by_id(db, product_update.id)
        if not db_product:
            return None
            
        for field, value in product_update.dict().items():
            setattr(db_product, field, value)
            
        db_product.updated_by = "system"
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
            
        products = query.all()
        return products

    def update_product_image_url(self, db: Session, product_id: int, image_url: str) -> Optional[Product]:
        db_product = self.get_product_by_id(db, product_id)
        if not db_product:
            return None

        db_product.image_url = image_url
        db.commit()
        db.refresh(db_product)
        return db_product

    def update_product_stock(
        self,
        db: Session,
        product_id: int,
        size: str,
        quantity_change: int
    ) -> Optional[ProductSize]:
        product_size = db.query(ProductSize).filter(
            ProductSize.product_id == product_id,
            ProductSize.size == size
        ).first()
        
        if not product_size:
            logger.error(f"Product size not found for product_id {product_id} and size {size}")
            raise HTTPException(status_code=404, detail="Product size not found")
        
        product_size.quantity += quantity_change
        if product_size.quantity < 0:
            logger.error(f"Insufficient stock for product_id {product_id} and size {size}")
            raise HTTPException(status_code=400, detail="Insufficient stock")
        
        db.commit()
        db.refresh(product_size)
        return product_size

    def add_default_category_discounts(
        self,
        db: Session,
        request: CategoryDiscountRequest
    ) -> List[CategoryDiscount]:
        discounts = []
        for category_id in request.category_ids:
            db_discount = db.query(CategoryDiscount).filter(
                CategoryDiscount.category_id == category_id
            ).first()

            if db_discount:
                db_discount.discounted_price = request.discounted_price
                db_discount.updated_by = "system"
            else:
                db_discount = CategoryDiscount(
                    category_id=category_id,
                    discounted_price=request.discounted_price,
                    created_by="system",
                    updated_by="system"
                )
                db.add(db_discount)
            discounts.append(db_discount)

        db.commit()
        for d in discounts:
            db.refresh(d)
        return discounts


    def get_category_discounts(self, db: Session, category_id: int) -> List[CategoryDiscount]:
        discounts = db.query(CategoryDiscount).filter(
            CategoryDiscount.category_id == category_id
        ).all()
        return discounts
    
    def get_default_category_discounts(self, db: Session) -> List[CategoryDiscount]:
        discounts = db.query(CategoryDiscount).all()
        return discounts