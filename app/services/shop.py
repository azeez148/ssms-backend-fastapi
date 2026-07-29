from sqlalchemy.orm import Session
from typing import List
from app.models.shop import Shop
from app.schemas.shop import ShopCreate

class ShopService:
    def create_shop(self, db: Session, shop: ShopCreate) -> Shop:
        db_shop = Shop(**shop.model_dump(), created_by="system", updated_by="system")
        db.add(db_shop)
        db.commit()
        db.refresh(db_shop)
        return db_shop

    def get_all_shops(self, db: Session) -> List[Shop]:
        return db.query(Shop).all()

    def get_shop_by_id(self, db: Session, shop_id: int) -> Shop:
        return db.query(Shop).filter(Shop.id == shop_id).first()

    def update_shop(self, db: Session, shop_id: int, shop: ShopCreate) -> Shop:
        db_shop = db.query(Shop).filter(Shop.id == shop_id).first()
        if db_shop:
            for key, value in shop.model_dump().items():
                setattr(db_shop, key, value)
            db_shop.updated_by = "system"
            db.commit()
            db.refresh(db_shop)
        return db_shop
