from sqlalchemy.orm import Session
from typing import List
from app.models.purchase import Purchase
from app.schemas.purchase import PurchaseCreate

class PurchaseService:
    def create_purchase(self, db: Session, purchase: PurchaseCreate) -> Purchase:
        db_purchase = Purchase(**purchase.dict())
        db.add(db_purchase)
        db.commit()
        db.refresh(db_purchase)
        return db_purchase

    def get_all_purchases(self, db: Session) -> List[Purchase]:
        return db.query(Purchase).all()

    def get_purchase_by_id(self, db: Session, purchase_id: int) -> Purchase:
        return db.query(Purchase).filter(Purchase.id == purchase_id).first()
