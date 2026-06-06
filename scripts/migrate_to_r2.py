import sys
import os

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.product import Product
from app.models.campaign import CampaignV2
from app.core.config import settings

def migrate_product_urls(db: Session, r2_base_url: str):
    products = db.query(Product).filter(Product.image_url.like("images/products/%")).all()
    print(f"Found {len(products)} products with local image paths.")

    updated_count = 0
    for product in products:
        old_url = product.image_url
        # Remove 'images/' prefix
        new_path = old_url.replace("images/", "", 1)
        new_url = f"{r2_base_url}/{new_path}"

        print(f"Updating product {product.id}: {old_url} -> {new_url}")
        product.image_url = new_url
        updated_count += 1
    return updated_count

def migrate_campaign_urls(db: Session, r2_base_url: str):
    campaigns = db.query(CampaignV2).filter(CampaignV2.image_url.like("images/campaigns/%")).all()
    print(f"Found {len(campaigns)} campaigns with local image paths.")

    updated_count = 0
    for campaign in campaigns:
        old_url = campaign.image_url
        # Remove 'images/' prefix
        new_path = old_url.replace("images/", "", 1)
        new_url = f"{r2_base_url}/{new_path}"

        print(f"Updating campaign {campaign.id}: {old_url} -> {new_url}")
        campaign.image_url = new_url
        updated_count += 1
    return updated_count

def main():
    if not settings.R2_PUBLIC_URL:
        print("Error: R2_PUBLIC_URL is not set in environment variables.")
        return

    r2_base_url = settings.R2_PUBLIC_URL.rstrip("/")
    db: Session = SessionLocal()
    try:
        product_updated = migrate_product_urls(db, r2_base_url)
        campaign_updated = migrate_campaign_urls(db, r2_base_url)

        db.commit()
        print(f"Successfully updated {product_updated} product URLs and {campaign_updated} campaign URLs.")

    except Exception as e:
        db.rollback()
        print(f"Error during migration: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
