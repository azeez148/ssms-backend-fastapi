import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

def init_database():
    # Get database configuration from environment variables or use defaults
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
    POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "ssms_db")

    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_SERVER,
        port=POSTGRES_PORT
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    # Create a cursor
    cur = conn.cursor()

    # Check if database exists
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (POSTGRES_DB,))
    exists = cur.fetchone()

    if not exists:
        # Create database if it doesn't exist
        cur.execute(f'CREATE DATABASE {POSTGRES_DB}')
        print(f"Database {POSTGRES_DB} created successfully!")
    else:
        print(f"Database {POSTGRES_DB} already exists.")

    # Close cursor and connection
    cur.close()
    conn.close()

if __name__ == "__main__":
    init_database()
