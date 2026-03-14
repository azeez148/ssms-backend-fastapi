import sys
import os
from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
import argparse

# Try to import from app, but provide fallback for standalone testing
try:
    from app.core.database import SessionLocal
    from app.models.sale import Sale, SaleItem
    from app.schemas.enums import SaleStatus
    Base = declarative_base() # Dummy Base for type hinting or fallback if needed
except ImportError:
    # Fallback for self-test or if not in app environment
    pass

# We'll define a separate Base for testing to avoid conflicts
TestBase = declarative_base()

class TestSale(TestBase):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    total_price = Column(Float)
    sub_total = Column(Float, nullable=True)
    sale_items = relationship("TestSaleItem", back_populates="sale")

class TestSaleItem(TestBase):
    __tablename__ = "sale_items"
    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer)
    sale_price = Column(Float)
    total_price = Column(Float)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    sale = relationship("TestSale", back_populates="sale_items")

def update_sales(db: Session, sale_model, dry_run=True):
    try:
        sales = db.query(sale_model).all()
        print(f"Total sales found: {len(sales)}")

        updated_sales_count = 0

        for sale in sales:
            sale_items = sale.sale_items
            if not sale_items:
                continue

            items_total_sum = sum(item.total_price if item.total_price is not None else 0 for item in sale_items)

            # Use a small epsilon for float comparison
            if abs(items_total_sum - (sale.total_price or 0)) > 0.01:
                print(f"Sale ID {sale.id}: mismatch! Sale Total: {sale.total_price}, Items Sum: {items_total_sum}")

                num_items = len(sale_items)
                target_total = sale.total_price or 0.0

                if num_items > 0:
                    new_item_total = round(target_total / num_items, 2)

                    running_sum = 0
                    for i in range(num_items - 1):
                        item = sale_items[i]
                        old_total = item.total_price
                        item.total_price = new_item_total
                        item.sale_price = round(item.total_price / item.quantity, 2) if (item.quantity and item.quantity > 0) else item.total_price
                        running_sum += item.total_price
                        print(f"  Item {item.id}: {old_total} -> {item.total_price} (sale_price: {item.sale_price}, qty: {item.quantity})")

                    # Last item gets the remainder
                    last_item = sale_items[-1]
                    old_total = last_item.total_price
                    last_item.total_price = round(target_total - running_sum, 2)
                    last_item.sale_price = round(last_item.total_price / last_item.quantity, 2) if (last_item.quantity and last_item.quantity > 0) else last_item.total_price
                    print(f"  Item {last_item.id} (last): {old_total} -> {last_item.total_price} (sale_price: {last_item.sale_price}, qty: {last_item.quantity})")

                    updated_sales_count += 1

        if not dry_run:
            if updated_sales_count > 0:
                db.commit()
                print(f"Successfully updated {updated_sales_count} sales.")
            else:
                print("No mismatches found. Nothing to update.")
        else:
            print(f"Dry run: {updated_sales_count} sales would have been updated.")
            db.rollback()

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()

def run_self_test():
    print("Running self-test with in-memory SQLite...")
    engine = create_engine("sqlite:///:memory:")
    TestBase.metadata.create_all(engine)
    SessionTest = sessionmaker(bind=engine)
    db = SessionTest()

    # Create a sale with mismatched item totals
    sale1 = TestSale(id=1, total_price=100.0)
    item1 = TestSaleItem(id=1, quantity=2, sale_price=20.0, total_price=40.0, sale=sale1)
    item2 = TestSaleItem(id=2, quantity=1, sale_price=50.0, total_price=50.0, sale=sale1)

    db.add(sale1)
    db.commit()

    print("Before update:")
    print(f"Sale 1 Total: {sale1.total_price}, Item 1 Total: {item1.total_price}, Item 2 Total: {item2.total_price}")

    update_sales(db, TestSale, dry_run=False)

    db.refresh(item1)
    db.refresh(item2)

    print("After update:")
    print(f"Sale 1 Total: {sale1.total_price}, Item 1 Total: {item1.total_price}, Item 2 Total: {item2.total_price}")

    assert abs(item1.total_price + item2.total_price - 100.0) < 0.001
    assert item1.total_price == 50.0
    assert item2.total_price == 50.0
    assert item1.sale_price == 25.0
    assert item2.sale_price == 50.0

    # Test with 3 items and rounding
    sale2 = TestSale(id=2, total_price=100.0)
    item3 = TestSaleItem(id=3, quantity=1, sale_price=33.0, total_price=33.0, sale=sale2)
    item4 = TestSaleItem(id=4, quantity=1, sale_price=33.0, total_price=33.0, sale=sale2)
    item5 = TestSaleItem(id=5, quantity=1, sale_price=33.0, total_price=33.0, sale=sale2)
    db.add(sale2)
    db.commit()

    update_sales(db, TestSale, dry_run=False)
    db.refresh(item3)
    db.refresh(item4)
    db.refresh(item5)

    print(f"Sale 2 (100.0) -> Items: {item3.total_price}, {item4.total_price}, {item5.total_price}")
    assert item3.total_price == 33.33
    assert item4.total_price == 33.33
    assert item5.total_price == 33.34
    assert abs(item3.total_price + item4.total_price + item5.total_price - 100.0) < 0.001

    print("Self-test passed!")
    db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update sale items total price to match sale total price.")
    parser.add_argument("--commit", action="store_true", help="Commit changes to the database.")
    parser.add_argument("--test", action="store_true", help="Run self-test.")
    args = parser.parse_args()

    if args.test:
        run_self_test()
    else:
        from app.core.database import SessionLocal
        from app.models.sale import Sale
        db = SessionLocal()
        try:
            update_sales(db, Sale, dry_run=not args.commit)
        finally:
            db.close()
