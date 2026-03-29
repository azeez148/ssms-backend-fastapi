from sqlalchemy import create_engine, inspect, text
import os

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "ssms-db")

# Allow overriding the entire URL via environment variable
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

def migrate_days_table():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    with engine.begin() as connection:
        # Use SQLAlchemy inspection to stay database-dialect agnostic.
        columns = [col["name"] for col in inspect(connection).get_columns("days")]

        if 'shop_id' not in columns:
            print("Adding shop_id column to days table...")
            connection.execute(text("ALTER TABLE days ADD COLUMN shop_id INTEGER REFERENCES shops(id)"))
        else:
            print("shop_id column already exists in days table.")

        # Update existing records to default shop_id 1
        print("Updating existing records to shop_id 1...")
        connection.execute(text("UPDATE days SET shop_id = 1 WHERE shop_id IS NULL"))

        print("Migration complete.")

if __name__ == "__main__":
    migrate_days_table()
