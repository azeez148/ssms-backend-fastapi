import os
import time
from sqlalchemy.orm import Session
from app.schemas.home import HomeResponse
from app.services.product import ProductService
from app.services.event import EventOfferService
from app.services.category import CategoryService
from app.models.event import EventOffer
from app.models.product import Product
from app.models.category import Category
from typing import List, Optional
import glob as glob_module

class HomeService:
    def __init__(self):
        self.product_service = ProductService()
        self.event_offer_service = EventOfferService()
        self.category_service = CategoryService()

    _home_cache = None
    _last_cache_time = 0
    CACHE_DURATION = 300  # 5 minutes

    def get_home_data(self, db: Session) -> HomeResponse:
        current_time = time.time()

        # Simple in-memory cache
        # We store the response as a Pydantic model which is already detached from DB session
        if self._home_cache and (current_time - self._last_cache_time < self.CACHE_DURATION):
            return self._home_cache

        products, total_count = self.product_service.get_all_products(db)
        # self._populate_product_images(products)

        # Ensure all nested objects are loaded before creating HomeResponse
        # HomeResponse(products=products) will trigger Pydantic to read all fields
        response = HomeResponse.model_validate(HomeResponse(products=products))

        self._home_cache = response
        self._last_cache_time = current_time

        return response

    def _populate_product_images(self, products: List[Product]):
        image_base_path = "images/products"  # base folder path

        # Pre-index the directory to avoid multiple disk I/O calls in a loop
        image_map = {}
        if os.path.exists(image_base_path):
            try:
                for entry in os.scandir(image_base_path):
                    if entry.is_dir():
                        product_id = entry.name
                        try:
                            with os.scandir(entry.path) as subentries:
                                for subentry in subentries:
                                    if subentry.is_file():
                                        image_map[product_id] = subentry.name
                                        break
                        except OSError:
                            pass
            except OSError:
                pass

        # for product in products:
        #     if not product.image_url:
        #         file_name = image_map.get(str(product.id))
        #         if file_name:
        #             product.image_url = f"images/products/{product.id}/{file_name}"
        #         else:
        #             # Fallback to a default image
        #             product.image_url = "images/products/default.jpg"

    def get_active_offers(self, db: Session) -> List[EventOffer]:
        return self.event_offer_service.get_active_event_offers(db)

    def get_weekly_offers(self, db: Session) -> List[Product]:
        offer = db.query(EventOffer).options(
            selectinload(EventOffer.products).options(
                joinedload(Product.category),
                selectinload(Product.shops),
                selectinload(Product.tags),
                selectinload(Product.size_map)
            )
        ).filter(EventOffer.code == "WEEKLY50OFF").first()

        if not offer:
            return []

        products = offer.products
        # self._populate_product_images(products)
        return products

    def get_categories(self, db: Session) -> List[Category]:
        return self.category_service.get_all_categories(db)

    # def search_products(self, db: Session, search: str) -> List[Product]:
    #     products, _ = self.product_service.get_all_products(db, search=search)
    #     return products

    def get_new_arrivals(self, db: Session) -> List[Product]:
        return db.query(Product).options(
            joinedload(Product.category),
            selectinload(Product.shops),
            selectinload(Product.tags),
            selectinload(Product.size_map)
        ).order_by(Product.created_date.desc()).limit(20).all()

    def get_offer_products(self, db: Session) -> List[Product]:
        return db.query(Product).options(
            joinedload(Product.category),
            selectinload(Product.shops),
            selectinload(Product.tags),
            selectinload(Product.size_map)
        ).filter(Product.offer_id.isnot(None)).all()

    def get_product_by_id(self, db: Session, product_id: int) -> Optional[Product]:
        return self.product_service.get_product_by_id(db, product_id)
    
    def get_products(self, db: Session, skip: int = 0, limit: Optional[int] = 50, category_id: Optional[int] = None, shop_id: Optional[int] = None, search: Optional[str] = None, has_image: Optional[bool] = None, is_in_stock: Optional[bool] = None, has_offer: Optional[bool] = None, tag_id: Optional[int] = None, sort_by: str = "newest") -> List[Product]:
        return self.product_service.get_all_products_minimal(
            db,
            skip=skip,
            limit=limit,
            category_id=category_id,
            shop_id=shop_id,
            search=search,
            has_image=has_image,
            is_in_stock=is_in_stock,
            has_offer=has_offer,
            tag_id=tag_id,
            sort_by=sort_by
        )