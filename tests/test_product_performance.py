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
        order_query = MagicMock()
        options_query = MagicMock()
        self.db.query.return_value = query
        query.order_by.return_value = order_query
        order_query.options.return_value = options_query
        options_query.offset.return_value = options_query
        options_query.all.return_value = []

        # Side effect to handle multiple calls to joinedload and selectinload
        def mock_joinedload_side_effect(attr):
            return f"joined_{attr}"
        def mock_selectinload_side_effect(attr):
            return f"selectin_{attr}"

        mock_joinedload.side_effect = mock_joinedload_side_effect
        mock_selectinload.side_effect = mock_selectinload_side_effect

        # Act
        self.product_service.get_all_products(self.db)

        # Assert
        self.db.query.assert_called_once_with(Product)
        options_query.offset.assert_called_once()
        order_query.options.assert_called_once_with(
            f"joined_{Product.category}",
            f"selectin_{Product.shops}",
            f"selectin_{Product.tags}",
            f"selectin_{Product.size_map}"
        )

if __name__ == "__main__":
    unittest.main()
