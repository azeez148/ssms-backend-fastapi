import unittest
from unittest.mock import MagicMock, patch

from app.models.product import Product
from app.services.product import ProductService


class TestProductEagerLoading(unittest.TestCase):
    def setUp(self):
        self.product_service = ProductService()
        self.db = MagicMock()

    @patch('app.services.product.selectinload')
    @patch('app.services.product.joinedload')
    def test_get_all_products_uses_eager_loading_for_shops_and_tags(self, mock_joinedload, mock_selectinload):
        # Arrange
        query = MagicMock()
        options_query = MagicMock()
        self.db.query.return_value = query
        query.options.return_value = options_query
        options_query.all.return_value = []

        mock_joinedload.return_value = "shops_loader"
        mock_selectinload.return_value = "tags_loader"

        # Act
        self.product_service.get_all_products(self.db)

        # Assert
        self.db.query.assert_called_once_with(Product)
        query.options.assert_called_once_with("shops_loader", "tags_loader")
        mock_joinedload.assert_called_once_with(Product.shops)
        mock_selectinload.assert_called_once_with(Product.tags)
        options_query.all.assert_called_once()


if __name__ == "__main__":
    unittest.main()
