import os
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from fastapi import HTTPException

from app.core.logging import logger
from app.models.product import Product
from app.models.product_size import ProductSize
from app.models.category_discount import CategoryDiscount
from app.models.shop import Shop
from app.schemas.product import (
    CategoryDiscountUpdateRequest,
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
        # Handle shop associations
        if product.shop_ids:
            shops = db.query(Shop).filter(Shop.id.in_(product.shop_ids)).all()
            db_product.shops = shops
        else:
            # Default to Shop ID 1 if no shops provided
            shop_1 = db.query(Shop).filter(Shop.id == 1).first()
            if shop_1:
                db_product.shops.append(shop_1)

        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product

    def get_all_products(self, db: Session) -> List[Product]:
        products = db.query(Product).options(joinedload(Product.shops)).all()
        return products

    def get_product_by_id(self, db: Session, product_id: int) -> Optional[Product]:
        product = db.query(Product).options(joinedload(Product.shops)).filter(Product.id == product_id).first()
        return product

    def update_product(self, db: Session, product_update: ProductUpdate) -> Optional[Product]:
        db_product = self.get_product_by_id(db, product_update.id)
        if not db_product:
            return None
            
        update_data = product_update.model_dump(exclude_unset=True)

        # Handle shop_ids separately
        if "shop_ids" in update_data:
            shop_ids = update_data.pop("shop_ids")
            if shop_ids is not None:
                shops = db.query(Shop).filter(Shop.id.in_(shop_ids)).all()
                db_product.shops = shops
            else:
                db_product.shops = []

        for field, value in update_data.items():
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
        query = db.query(Product).options(joinedload(Product.shops))
        
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
        db_discount = db.query(CategoryDiscount).filter(
            CategoryDiscount.category_id == request.category_id
        ).first()

        if db_discount:
            db_discount.discounted_price = request.discounted_price
            db_discount.updated_by = "system"
        else:
            db_discount = CategoryDiscount(
                category_id=request.category_id,
                discounted_price=request.discounted_price,
                created_by="system",
                updated_by="system"
            )
            db.add(db_discount)

        db.commit()
        db.refresh(db_discount)
        return self.get_category_discounts(db, request.category_id)


    def get_category_discounts(self, db: Session, category_id: int) -> List[CategoryDiscount]:
        discounts = db.query(CategoryDiscount).filter(
            CategoryDiscount.category_id == category_id
        ).all()
        return discounts
    
    def get_default_category_discounts(self, db: Session) -> List[CategoryDiscount]:
        discounts = db.query(CategoryDiscount).all()
        return discounts
    
    def update_category_discount(self, db: Session, request: CategoryDiscountUpdateRequest) -> List[CategoryDiscount]:
        db_discount = db.query(CategoryDiscount).filter(
            CategoryDiscount.id == request.id,
            CategoryDiscount.category_id == request.category_id
        ).first()

        if not db_discount:
            logger.error(f"Category discount not found for id {request.id} and category_id {request.category_id}")
            raise HTTPException(status_code=404, detail="Category discount not found")

        db_discount.discounted_price = request.discounted_price
        db_discount.updated_by = "system"
        db.commit()
        db.refresh(db_discount)

        return self.get_category_discounts(db, request.category_id)
    