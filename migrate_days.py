from sqlalchemy import create_engine, text
import os

# Database connection URL - defaulting to SQLite for this environment but typically set via DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ssms.db")

def migrate_days_table():
    engine = create_engine(DATABASE_URL)

    with engine.connect() as connection:
        # Check if shop_id column exists
        inspector = text("PRAGMA table_info(days)")
        result = connection.execute(inspector)
        columns = [row[1] for row in result.fetchall()]

        if 'shop_id' not in columns:
            print("Adding shop_id column to days table...")
            connection.execute(text("ALTER TABLE days ADD COLUMN shop_id INTEGER REFERENCES shops(id)"))
            connection.commit()
        else:
            print("shop_id column already exists in days table.")

        # Update existing records to default shop_id 1
        print("Updating existing records to shop_id 1...")
        connection.execute(text("UPDATE days SET shop_id = 1 WHERE shop_id IS NULL"))
        connection.commit()

        print("Migration complete.")

if __name__ == "__main__":
    migrate_days_table()
