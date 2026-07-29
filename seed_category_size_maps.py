import json
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.category import Category

size_maps = {
    "Jersey": ["S", "M", "L", "XL", "XXL"],
    "Five Sleeve Jersey": ["S", "M", "L", "XL", "XXL"],
    "Full Sleeve Jersey": ["S", "M", "L", "XL", "XXL"],
    "Kids Jersey": ["20", "22", "24", "26", "28", "30", "32", "34"],
    "First Copy Jersey": ["S", "M", "L", "XL", "XXL"],
    "Tshirt": ["S", "M", "L", "XL", "XXL"],
    "Dotknit Shorts - Embroidery": ["S", "M", "L", "XL", "XXL"],
    "Dotknit Shorts - Submiation": ["S", "M", "L", "XL", "XXL"],
    "Dotknit Shorts - Plain": ["S", "M", "L", "XL", "XXL"],
    "PP Shorts - Plain": ["S", "M", "L", "XL", "XXL"],
    "PP Shorts - Embroidery": ["S", "M", "L", "XL", "XXL"],
    "FC Shorts": ["S", "M", "L", "XL", "XXL"],
    "NS Shorts": ["S", "M", "L", "XL", "XXL"],
    "Sleeve Less - D/N": ["S", "M", "L", "XL", "XXL"],
    "Sleeve Less - Saleena": ["S", "M", "L", "XL", "XXL"],
    "Sleeve Less - Other": ["S", "M", "L", "XL", "XXL"],
    "Sleeve Less - NS": ["S", "M", "L", "XL", "XXL"],
    "Track Pants - Imp": ["S", "M", "L", "XL", "XXL"],
    "Track Pants - Normal": ["S", "M", "L", "XL", "XXL"],
    "Boot-Adult": ["5", "5.5", "6", "6.5", "7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11"],
    "Boot-Kids": ["-13", "-12", "-11", "1", "2", "3", "4"],
    "Boot-Imp": ["5", "5.5", "6", "6.5", "7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11"],
    "Shorts-Kids": ["20", "22", "24", "26", "28", "30", "32", "34"],
    "Football": ["3", "4", "5"],
    "Cricket Ball": ["Standard"],
    "Shuttle Bat": ["Standard"],
    "Shuttle Cock": ["Standard"],
    "Foot Pad": ["Free Size"],
    "Foot sleeve": ["Free Size"],
    "Socks-Full": ["Free Size"],
    "Socks-3/4": ["Free Size"],
    "Socks-Half": ["Free Size"],
    "Socks-Ankle": ["Free Size"],
    "Hand Sleeve": ["Free Size"],
    "GK Glove": ["5.5", "6", "6.5", "7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11"],
    "Trophy": ["Small", "Medium", "Large"]
}

def seed_size_maps():
    db = SessionLocal()
    try:
        for category_name, sizes in size_maps.items():
            size_map_str = ",".join(sizes)
            category = db.query(Category).filter(Category.name == category_name).first()
            if category:
                print(f"Updating size_map for category: {category_name}")
                category.size_map = size_map_str
                category.updated_by = "seeding_script"
            else:
                print(f"Creating new category: {category_name}")
                new_category = Category(
                    name=category_name,
                    size_map=size_map_str,
                    created_by="seeding_script",
                    updated_by="seeding_script"
                )
                db.add(new_category)
        db.commit()
        print("Seeding completed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_size_maps()
