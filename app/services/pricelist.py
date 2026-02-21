from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.pricelist import Pricelist
from app.schemas.pricelist import PricelistCreate, PricelistUpdate

class PricelistService:
    def create_pricelist(self, db: Session, pricelist_data: PricelistCreate) -> Pricelist:
        db_pricelist = Pricelist(
            category_id=pricelist_data.category_id,
            unit_price=pricelist_data.unit_price,
            selling_price=pricelist_data.selling_price,
            discounted_price=pricelist_data.discounted_price,
            created_by="system",
            updated_by="system"
        )
        db.add(db_pricelist)
        db.commit()
        db.refresh(db_pricelist)
        return db_pricelist

    def get_all_pricelists(self, db: Session) -> List[Pricelist]:
        return db.query(Pricelist).all()

    def get_pricelist_by_id(self, db: Session, pricelist_id: int) -> Optional[Pricelist]:
        return db.query(Pricelist).filter(Pricelist.id == pricelist_id).first()

    def get_pricelist_by_category_id(self, db: Session, category_id: int) -> Optional[Pricelist]:
        return db.query(Pricelist).filter(Pricelist.category_id == category_id).first()

    def update_pricelist(self, db: Session, pricelist_id: int, pricelist_data: PricelistUpdate) -> Optional[Pricelist]:
        db_pricelist = self.get_pricelist_by_id(db, pricelist_id)
        if not db_pricelist:
            return None

        update_data = pricelist_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_pricelist, key, value)

        db_pricelist.updated_by = "system"
        db.commit()
        db.refresh(db_pricelist)
        return db_pricelist

    def delete_pricelist(self, db: Session, pricelist_id: int) -> bool:
        db_pricelist = self.get_pricelist_by_id(db, pricelist_id)
        if not db_pricelist:
            return False

        db.delete(db_pricelist)
        db.commit()
        return True
