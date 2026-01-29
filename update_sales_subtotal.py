import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the current directory to the path so we can import app
sys.path.append(os.getcwd())

from app.models.sale import Sale, SaleItem
from app.models.product import Product

def update_sales_subtotal(db_url=None):
    if db_url:
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db = Session()
    else:
        from app.core.database import SessionLocal
        db = SessionLocal()

    try:
        # Fetch all sales
        sales = db.query(Sale).all()
        print(f"Found {len(sales)} sales to process.")

        updated_count = 0
        for sale in sales:
            calculated_sub_total = 0.0
            print(f"Processing Sale ID: {sale.id}")

            # Fetch all items for this sale
            sale_items = sale.sale_items

            if not sale_items:
                print(f"  No items found for Sale ID: {sale.id}")
                # We still update it to 0.0 if that's what's calculated
            else:
                for item in sale_items:
                    # Find product selling price using product_id
                    product = db.query(Product).filter(Product.id == item.product_id).first()

                    if product:
                        # Selling price from product table
                        selling_price = product.selling_price if product.selling_price is not None else 0.0
                        item_total = selling_price * item.quantity
                        calculated_sub_total += item_total
                        print(f"  Item ID: {item.id}, Product ID: {item.product_id}, Name: {product.name}, Qty: {item.quantity}, Product Selling Price: {selling_price}, Item Total: {item_total}")
                    else:
                        print(f"  Warning: Product ID {item.product_id} not found in products table for Sale Item ID {item.id}. Using item's sale_price as fallback.")
                        item_total = (item.sale_price if item.sale_price is not None else 0.0) * item.quantity
                        calculated_sub_total += item_total

            print(f"  Old sub_total: {sale.sub_total}, New calculated sub_total: {calculated_sub_total}")
            sale.sub_total = float(calculated_sub_total)
            updated_count += 1

        db.commit()
        print(f"Successfully updated sub_total for {updated_count} sales.")

    except Exception as e:
        db.rollback()
        print(f"An error occurred during update: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # If a database URL is provided as an argument, use it.
    # Otherwise use the default from app.core.database
    url = sys.argv[1] if len(sys.argv) > 1 else None
    update_sales_subtotal(url)
