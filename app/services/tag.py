from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.tag import Tag
from app.models.product import Product
from app.schemas.tag import TagCreate, TagUpdate, TagMapRequest

class TagService:
    def get_all_tags(self, db: Session) -> List[Tag]:
        return db.query(Tag).all()

    def create_tag(self, db: Session, tag_data: TagCreate) -> Tag:
        db_tag = Tag(
            name=tag_data.name,
            description=tag_data.description,
            created_by="system",
            updated_by="system"
        )
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return db_tag

    def update_tag(self, db: Session, tag_data: TagUpdate) -> Optional[Tag]:
        db_tag = db.query(Tag).filter(Tag.id == tag_data.id).first()
        if not db_tag:
            return None

        db_tag.name = tag_data.name
        db_tag.description = tag_data.description
        db_tag.updated_by = "system"

        db.commit()
        db.refresh(db_tag)
        return db_tag

    def delete_tag(self, db: Session, tag_id: int) -> bool:
        db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not db_tag:
            return False

        db.delete(db_tag)
        db.commit()
        return True

    def map_tags_to_products(self, db: Session, map_data: TagMapRequest):
        products = db.query(Product).filter(Product.id.in_(map_data.productIds)).all()
        tags = db.query(Tag).filter(Tag.id.in_(map_data.tagIds)).all()

        for product in products:
            # Add tags that are not already present
            for tag in tags:
                if tag not in product.tags:
                    product.tags.append(tag)

        db.commit()
        return {"message": f"Successfully mapped {len(tags)} tags to {len(products)} products"}
