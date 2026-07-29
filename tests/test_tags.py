import unittest
from unittest.mock import MagicMock
from app.services.tag import TagService
from app.schemas.tag import TagCreate, TagUpdate, TagMapRequest
from app.models.tag import Tag
from app.models.product import Product

class TestTags(unittest.TestCase):

    def setUp(self):
        self.tag_service = TagService()
        self.db_session = MagicMock()

    def test_create_tag(self):
        tag_data = TagCreate(name="New Tag", description="Description")

        # Act
        db_tag = self.tag_service.create_tag(self.db_session, tag_data)

        # Assert
        self.db_session.add.assert_called()
        self.db_session.commit.assert_called()
        self.assertEqual(db_tag.name, "New Tag")
        self.assertEqual(db_tag.description, "Description")

    def test_update_tag(self):
        # Arrange
        db_tag = Tag(id=1, name="Old Name", description="Old Desc")
        self.db_session.query.return_value.filter.return_value.first.return_value = db_tag

        update_data = TagUpdate(id=1, name="New Name", description="New Desc")

        # Act
        updated_tag = self.tag_service.update_tag(self.db_session, update_data)

        # Assert
        self.assertEqual(updated_tag.name, "New Name")
        self.assertEqual(updated_tag.description, "New Desc")
        self.db_session.commit.assert_called()

    def test_map_tags_to_products(self):
        # Arrange
        product1 = Product(id=1, name="Product 1", tags=[])
        product2 = Product(id=2, name="Product 2", tags=[])
        tag1 = Tag(id=1, name="Tag 1")

        # Mock query for products
        self.db_session.query.return_value.filter.return_value.all.side_effect = [
            [product1, product2], # First call for products
            [tag1]                # Second call for tags
        ]

        map_data = TagMapRequest(productIds=[1, 2], tagIds=[1])

        # Act
        result = self.tag_service.map_tags_to_products(self.db_session, map_data)

        # Assert
        self.assertIn(tag1, product1.tags)
        self.assertIn(tag1, product2.tags)
        self.db_session.commit.assert_called()

    def test_unmap_tags_from_products(self):
        # Arrange
        tag1 = Tag(id=1, name="Tag 1")
        product1 = Product(id=1, name="Product 1", tags=[tag1])

        self.db_session.query.return_value.filter.return_value.all.side_effect = [
            [product1], # First call for products
            [tag1]      # Second call for tags
        ]

        map_data = TagMapRequest(productIds=[1], tagIds=[1])

        # Act
        result = self.tag_service.unmap_tags_from_products(self.db_session, map_data)

        # Assert
        self.assertNotIn(tag1, product1.tags)
        self.db_session.commit.assert_called()

if __name__ == '__main__':
    unittest.main()
