import sys
import os
from collections import defaultdict
from sqlalchemy.orm import Session
from datetime import datetime

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.product import Product

def flag_duplicates():
    db: Session = SessionLocal()
    try:
        # 1. Scan for identical product names
        # We only care about active products? User didn't specify, so let's check all.
        products = db.query(Product).order_by(Product.created_date, Product.id).all()

        name_groups = defaultdict(list)
        for p in products:
            name_groups[p.name].append(p)

        report = []
        total_duplicates = 0

        for name, group in name_groups.items():
            if len(group) > 1:
                # The group is already sorted by created_date, then id.
                parent = group[0]
                duplicates = group[1:]

                report.append(f"Product Group: '{name}'")
                report.append(f"  Parent: ID={parent.id}, Created={parent.created_date}")

                for dup in duplicates:
                    dup.is_duplicate = True
                    dup.parent_product_id = parent.id
                    total_duplicates += 1
                    report.append(f"  Duplicate: ID={dup.id}, Created={dup.created_date} -> Flagged (Parent ID={parent.id})")

                report.append("")

        db.commit()

        print("--- Deduplication Report ---")
        if total_duplicates == 0:
            print("No duplicates found.")
        else:
            print(f"Total duplicates flagged: {total_duplicates}")
            print("\n".join(report))
        print("----------------------------")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    flag_duplicates()
