import os
from sqlalchemy.orm import Session
from app.schemas.home import HomeResponse
from app.services.product import ProductService
from app.services.event import EventOfferService
from app.models.event import EventOffer
from typing import List
import glob as glob_module

class HomeService:
    def __init__(self):
        self.product_service = ProductService()
        self.event_offer_service = EventOfferService()

    def get_home_data(self, db: Session) -> HomeResponse:
        products = self.product_service.get_all_products(db)
        image_base_path = "images/products"  # base folder path

        for product in products:
            if not product.image_url:
                # Folder path for this product
                product_folder = os.path.join(image_base_path, str(product.id))

                # Match any image file inside that folder
                pattern = os.path.join(product_folder, "*.*")
                matching_files = glob_module.glob(pattern)

                if matching_files:
                    # Pick the first file (you can sort or filter if needed)
                    file_name = os.path.basename(matching_files[0])
                    product.image_url = f"images/products/{product.id}/{file_name}"
                else:
                    # Fallback to a default image
                    product.image_url = "images/products/default.jpg"

        return HomeResponse(products=products)

    def get_active_offers(self, db: Session) -> List[EventOffer]:
        return self.event_offer_service.get_active_event_offers(db)
