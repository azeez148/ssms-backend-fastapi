from sqlalchemy.orm import Session
from typing import List
from app.models.category import Category
from app.schemas.category import CategoryCreate

class CategoryService:
    def create_category(self, db: Session, category: CategoryCreate) -> Category:
        db_category = Category(
            name=category.name,
            description=category.description
        )
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category

    def get_all_categories(self, db: Session) -> List[Category]:
        return db.query(Category).all()

    def get_category_by_id(self, db: Session, category_id: int) -> Category:
        return db.query(Category).filter(Category.id == category_id).first()
