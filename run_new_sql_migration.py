import psycopg2
from app.core import database

def execute_sql_file(filename):
    # Connect to the database
    conn = psycopg2.connect(
        dbname=database.POSTGRES_DB,
        user=database.POSTGRES_USER,
        password=database.POSTGRES_PASSWORD,
        host=database.POSTGRES_SERVER,
    )
    cur = conn.cursor()

    with open(filename, 'r') as f:
        cur.execute(f.read())

    conn.commit()
    cur.close()
    conn.close()

def run_sql_migrations():
    print("Running Update...")
    execute_sql_file('products_new.sql')
    print("Migrations completed!")

if __name__ == "__main__":
    run_sql_migrations()
    print("Migrations complete!")
