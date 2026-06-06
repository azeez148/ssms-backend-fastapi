import sys
import os

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.product import Product
from app.core.config import settings

def migrate_product_urls():
    db: Session = SessionLocal()
    try:
        products = db.query(Product).filter(Product.image_url.like("images/products/%")).all()
        print(f"Found {len(products)} products with local image paths.")

        if not settings.R2_PUBLIC_URL:
            print("Error: R2_PUBLIC_URL is not set in environment variables.")
            return

        r2_base_url = settings.R2_PUBLIC_URL.rstrip("/")

        updated_count = 0
        for product in products:
            # Local path format: images/products/{id}/{filename}
            # We want to change it to: {r2_base_url}/products/{filename}
            # or keep the structure: {r2_base_url}/products/{id}/{filename}

            # The current implementation of StorageService uploads to {folder}/{unique_filename}
            # If the user manually moves files, they might want to keep the structure or change it.
            # Assuming they move 'images/products/*' to 'products/*' in R2.

            old_url = product.image_url
            # Remove 'images/' prefix
            new_path = old_url.replace("images/", "", 1)
            new_url = f"{r2_base_url}/{new_path}"

            print(f"Updating product {product.id}: {old_url} -> {new_url}")
            product.image_url = new_url
            updated_count += 1

        db.commit()
        print(f"Successfully updated {updated_count} product image URLs.")

    except Exception as e:
        db.rollback()
        print(f"Error during migration: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_product_urls()
