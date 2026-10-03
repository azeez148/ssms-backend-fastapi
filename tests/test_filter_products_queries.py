import os
# Set DATABASE_URL before importing anything that uses it
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from typing import List
import pytest
from pydantic import TypeAdapter
from sqlalchemy import event

from app.core.database import SessionLocal, engine, Base
from app.services.product import ProductService
from app.schemas.product import ProductResponse
from app.models.product import Product
from app.models.product_size import ProductSize
from app.models.shop import Shop
from app.models.category import Category
from app.models.tag import Tag


def _count_statements_for_filter(db, category_id=None):
    """Statements issued by the service call plus response serialization."""
    count = {"n": 0}

    def _counter(*args):
        count["n"] += 1

    event.listen(engine, "before_cursor_execute", _counter)
    try:
        products = ProductService().get_filtered_products(db, category_id, None)
        adapter = TypeAdapter(List[ProductResponse])
        data = adapter.dump_python(adapter.validate_python(products))
    finally:
        event.remove(engine, "before_cursor_execute", _counter)
    return data, count["n"]


# This test drops and recreates tables, so it must never run against a real
# database (another test module may have created the engine before DATABASE_URL was set).
@pytest.mark.skipif(engine.dialect.name != "sqlite", reason="requires the SQLite test database")
def test_filter_products_query_count_does_not_grow_with_products():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        categories = [Category(name=f"FC{i}", description="d") for i in range(3)]
        shop = Shop(name="FS", shop_code="FS", addressLine1="a", addressLine2="b", city="c",
                    state="s", country="IN", zipcode="1", mobileNumber="1", email="e")
        tags = [Tag(name=f"FT{i}") for i in range(2)]
        db.add_all(categories + [shop] + tags)
        db.flush()
        for i in range(30):
            product = Product(name=f"FP{i}", unit_price=10, selling_price=12,
                              category_id=categories[i % 3].id)
            product.shops = [shop]
            product.tags = tags[: i % 3]
            product.size_map = [ProductSize(size="M", quantity=i)]
            db.add(product)
        db.commit()
        first_category_id = categories[0].id
        db.expunge_all()

        data, statements = _count_statements_for_filter(db)

        assert len(data) == 30
        assert all(p["category"]["id"] == p["category_id"] for p in data)
        assert any(p["tags"] for p in data)
        assert all(p["shops"][0]["name"] == "FS" for p in data)
        assert all(len(p["size_map"]) == 1 for p in data)
        # Fixed number of eager-load queries; previously this was 1 + N + categories.
        assert statements <= 5, f"N+1 regression: {statements} statements for 30 products"

        db.expunge_all()
        filtered, _ = _count_statements_for_filter(db, category_id=first_category_id)
        assert len(filtered) == 10
        assert all(p["category_id"] == first_category_id for p in filtered)
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
