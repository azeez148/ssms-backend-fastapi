from sqlalchemy.orm import Session
from typing import List
from app.models.delivery import DeliveryType
from app.schemas.delivery import DeliveryTypeCreate

class DeliveryTypeService:
    def create_delivery_type(self, db: Session, delivery_type: DeliveryTypeCreate) -> DeliveryType:
        db_delivery_type = DeliveryType(**delivery_type.dict(), created_by="system", updated_by="system")
        db.add(db_delivery_type)
        db.commit()
        db.refresh(db_delivery_type)
        return db_delivery_type

    def get_all_delivery_types(self, db: Session) -> List[DeliveryType]:
        return db.query(DeliveryType).all()

    def get_delivery_type_by_id(self, db: Session, delivery_type_id: int) -> DeliveryType:
        return db.query(DeliveryType).filter(DeliveryType.id == delivery_type_id).first()
