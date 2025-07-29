from sqlalchemy.orm import Session
from app.schemas.home import HomeResponse
from app.services.product import ProductService

class HomeService:
    def __init__(self):
        self.product_service = ProductService()

    def get_home_data(self, db: Session) -> HomeResponse:
        products = self.product_service.get_all_products(db)
        return HomeResponse(products=products)
