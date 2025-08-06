import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from app.core import database

def init_database():
    # Get database configuration from environment variables or use defaults

    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        user=database.POSTGRES_USER,
        password=database.POSTGRES_PASSWORD,
        host=database.POSTGRES_SERVER,
        port=database.POSTGRES_PORT
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    # Create a cursor
    cur = conn.cursor()

    # Check if database exists
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (database.POSTGRES_DB,))
    exists = cur.fetchone()

    if not exists:
        # Create database if it doesn't exist
        cur.execute(f'CREATE DATABASE {database.POSTGRES_DB}')
        print(f"Database {database.POSTGRES_DB} created successfully!")
    else:
        print(f"Database {database.POSTGRES_DB} already exists.")

    # Close cursor and connection
    cur.close()
    conn.close()

if __name__ == "__main__":
    init_database()
