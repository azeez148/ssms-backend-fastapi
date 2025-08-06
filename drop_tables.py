import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.core import database
def drop_all_tables():
    # Connect to the database
    conn = psycopg2.connect(
        dbname=database.POSTGRES_DB,
        user=database.POSTGRES_USER,
        password=database.POSTGRES_PASSWORD,
        host=database.POSTGRES_SERVER,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Drop all tables
    cur.execute("""
        DO $$ 
        DECLARE 
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) 
            LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
    """)
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    drop_all_tables()
    print("All tables dropped successfully!")
