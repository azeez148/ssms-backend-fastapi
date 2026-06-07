import sys
import os
import boto3
import uuid
import magic
from botocore.config import Config
from sqlalchemy.orm import Session

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.product import Product
from app.models.campaign import CampaignV2
from app.core.config import settings

class R2Migrator:
    def __init__(self):
        if not all([settings.R2_ACCOUNT_ID, settings.R2_ACCESS_KEY_ID, settings.R2_SECRET_ACCESS_KEY]):
            print("Error: Cloudflare R2 credentials are not fully configured in environment variables.")
            print(f"R2_ACCOUNT_ID: {'Set' if settings.R2_ACCOUNT_ID else 'Not Set'}")
            print(f"R2_ACCESS_KEY_ID: {'Set' if settings.R2_ACCESS_KEY_ID else 'Not Set'}")
            print(f"R2_SECRET_ACCESS_KEY: {'Set' if settings.R2_SECRET_ACCESS_KEY else 'Not Set'}")
            sys.exit(1)

        self.s3_client = boto3.client(
            service_name="s3",
            endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3v4"),
            region_name="auto"
        )
        self.bucket_name = settings.R2_BUCKET_NAME
        # The project root is one level up from this script
        self.local_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(f"Project root directory: {self.local_base_dir}")

    def upload_to_r2(self, local_path, folder):
        if not os.path.exists(local_path):
            print(f"  Warning: Local file not found at: {local_path}")
            return None

        try:
            with open(local_path, "rb") as f:
                content = f.read()

            if not content:
                print(f"  Warning: File is empty: {local_path}")
                return None

            content_type = magic.from_buffer(content, mime=True)
            ext = os.path.splitext(local_path)[1].lower()
            if not ext:
                # Try to guess extension from content type
                if content_type == "image/jpeg": ext = ".jpg"
                elif content_type == "image/png": ext = ".png"
                elif content_type == "image/webp": ext = ".webp"
                else: ext = ".bin"

            new_filename = f"{uuid.uuid4()}{ext}"
            object_key = f"{folder}/{new_filename}"

            print(f"  Uploading {os.path.basename(local_path)} to R2 as {object_key} (Type: {content_type})...")
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=content,
                ContentType=content_type
            )
            print(f"  Successfully uploaded to R2: {object_key}")
            return object_key
        except Exception as e:
            print(f"  Error uploading {local_path}: {e}")
            return None

    def migrate_products(self, db: Session):
        print("\n--- Migrating Product Images ---")
        # Find products with local image URLs
        # We look for image_url that doesn't start with 'http' and isn't already a key (doesn't start with 'products/')
        products = db.query(Product).filter(
            Product.image_url.isnot(None),
            Product.image_url != "",
            ~Product.image_url.like("http%"),
            ~Product.image_url.like("products/%")
        ).all()

        print(f"Found {len(products)} products potentially needing migration.")

        count = 0
        for product in products:
            print(f"Processing Product ID: {product.id}, Name: {product.name}")
            old_path = product.image_url

            # Logic to find the file
            possible_paths = [
                os.path.join(self.local_base_dir, old_path),
                os.path.join(self.local_base_dir, "images", "products", old_path) if not old_path.startswith("images") else "",
                os.path.join(self.local_base_dir, "images", old_path) if not old_path.startswith("images") else ""
            ]

            local_path = None
            for p in possible_paths:
                if p and os.path.exists(p) and os.path.isfile(p):
                    local_path = p
                    break

            if not local_path:
                print(f"  Error: Could not find local file for product {product.id} (URL: {old_path})")
                continue

            new_key = self.upload_to_r2(local_path, "products")
            if new_key:
                print(f"  Updating DB: {old_path} -> {new_key}")
                product.image_url = new_key
                count += 1
            else:
                print(f"  Failed to upload image for product {product.id}")

        return count

    def migrate_campaigns(self, db: Session):
        print("\n--- Migrating Campaign Images ---")
        campaigns = db.query(CampaignV2).filter(
            CampaignV2.image_url.isnot(None),
            CampaignV2.image_url != "",
            ~CampaignV2.image_url.like("http%"),
            ~CampaignV2.image_url.like("campaigns/%")
        ).all()

        print(f"Found {len(campaigns)} campaigns potentially needing migration.")

        count = 0
        for campaign in campaigns:
            print(f"Processing Campaign ID: {campaign.id}, Title: {campaign.title}")
            old_path = campaign.image_url

            possible_paths = [
                os.path.join(self.local_base_dir, old_path),
                os.path.join(self.local_base_dir, "images", "campaigns", old_path) if not old_path.startswith("images") else "",
                os.path.join(self.local_base_dir, "images", old_path) if not old_path.startswith("images") else ""
            ]

            local_path = None
            for p in possible_paths:
                if p and os.path.exists(p) and os.path.isfile(p):
                    local_path = p
                    break

            if not local_path:
                print(f"  Error: Could not find local file for campaign {campaign.id} (URL: {old_path})")
                continue

            new_key = self.upload_to_r2(local_path, "campaigns")
            if new_key:
                print(f"  Updating DB: {old_path} -> {new_key}")
                campaign.image_url = new_key
                count += 1
            else:
                print(f"  Failed to upload image for campaign {campaign.id}")

        return count

def main():
    try:
        migrator = R2Migrator()
    except SystemExit:
        return

    db = SessionLocal()
    try:
        product_count = migrator.migrate_products(db)
        campaign_count = migrator.migrate_campaigns(db)

        db.commit()
        print(f"\nMigration Summary:")
        print(f"Products migrated: {product_count}")
        print(f"Campaigns migrated: {campaign_count}")
        print("Migration completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
