from sqlalchemy.orm import Session
from typing import List
from app.models.payment import PaymentType
from app.schemas.payment import PaymentTypeCreate

class PaymentTypeService:
    def create_payment_type(self, db: Session, payment_type: PaymentTypeCreate) -> PaymentType:
        db_payment_type = PaymentType(**payment_type.dict(), created_by="system", updated_by="system")
        db.add(db_payment_type)
        db.commit()
        db.refresh(db_payment_type)
        return db_payment_type

    def get_all_payment_types(self, db: Session) -> List[PaymentType]:
        return db.query(PaymentType).all()

    def get_payment_type_by_id(self, db: Session, payment_type_id: int) -> PaymentType:
        return db.query(PaymentType).filter(PaymentType.id == payment_type_id).first()
