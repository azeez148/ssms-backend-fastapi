import os
# Set DATABASE_URL before importing anything that uses it
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.core.database import SessionLocal, engine, Base
from app.services.product import ProductService
from app.schemas.product import ProductCreate, ProductSizeBase
from app.models.product import Product
from app.models.shop import Shop
from app.models.category import Category
from app.models.tag import Tag
from app.models.event import EventOffer, EventOfferType, RateType

def test_product_filters_and_ordering():
    # Create tables in SQLite
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    product_service = ProductService()

    try:
        # 1. Setup: Create test data
        category = Category(name="Test Category", description="Test")
        db.add(category)
        db.commit()
        db.refresh(category)

        shop = Shop(name="Test Shop", shop_code="TS")
        db.add(shop)
        db.commit()
        db.refresh(shop)

        # Create products with different attributes
        p1_data = ProductCreate(
            name="Alpha Product",
            description="First",
            unit_price=100,
            selling_price=120,
            category_id=category.id,
            size_map=[ProductSizeBase(size="M", quantity=10)],
            shop_ids=[shop.id]
        )
        p2_data = ProductCreate(
            name="Beta Product",
            description="Second",
            unit_price=200,
            selling_price=220,
            category_id=category.id,
            size_map=[ProductSizeBase(size="M", quantity=0)], # Out of stock
            shop_ids=[shop.id]
        )

        prod1 = product_service.create_product(db, p1_data)
        prod2 = product_service.create_product(db, p2_data)

        # Add image to prod1
        prod1.image_url = "http://example.com/image.jpg"

        # Add offer to prod2
        offer = EventOffer(
            name="Test Offer",
            description="Test",
            type=EventOfferType.offer,
            rate_type=RateType.percentage,
            rate=10
        )
        db.add(offer)
        db.commit()
        db.refresh(offer)
        prod2.offer_id = offer.id
        db.commit()

        # Add tag to prod1
        tag = Tag(name="Test Tag")
        db.add(tag)
        db.commit()
        db.refresh(tag)
        prod1.tags.append(tag)
        db.commit()

        # 2. Test Default Ordering (Newest first)
        products, total = product_service.get_all_products_minimal(db)
        assert len(products) >= 2
        assert products[0].id > products[1].id

        # 3. Test Oldest Ordering
        products, total = product_service.get_all_products_minimal(db, sort_by="oldest")
        assert products[0].id < products[1].id

        # 4. Test has_image filter
        products, total = product_service.get_all_products_minimal(db, has_image=True)
        assert len(products) > 0
        assert all(p.image_url for p in products)

        products, total = product_service.get_all_products_minimal(db, has_image=False)
        assert len(products) > 0
        assert all(not p.image_url for p in products)

        # 5. Test is_in_stock filter
        products, total = product_service.get_all_products_minimal(db, is_in_stock=True)
        assert len(products) > 0
        assert all(p.is_in_stock for p in products)

        products, total = product_service.get_all_products_minimal(db, is_in_stock=False)
        assert len(products) > 0
        assert all(not p.is_in_stock for p in products)

        # 6. Test has_offer filter
        products, total = product_service.get_all_products_minimal(db, has_offer=True)
        assert len(products) > 0
        assert all(p.offer_id for p in products)

        # 7. Test tag_id filter
        products, total = product_service.get_all_products(db, tag_id=tag.id)
        assert len(products) >= 1
        assert any(t.id == tag.id for p in products for t in p.tags)

        print("All tests passed successfully!")

    finally:
        db.close()
        # Clean up test database
        if os.path.exists("./test.db"):
            os.remove("./test.db")

if __name__ == "__main__":
    test_product_filters_and_ordering()
