import psycopg2
from drop_tables import drop_all_tables
from create_tables import create_tables

def execute_sql_file(filename):
    # Connect to the database
    conn = psycopg2.connect(
        dbname='ssms-db',
        user='postgres',
        password='admin',
        host='localhost'
    )
    cur = conn.cursor()

    with open(filename, 'r') as f:
        cur.execute(f.read())

    conn.commit()
    cur.close()
    conn.close()

def reset_database():
    print("Dropping all tables...")
    drop_all_tables()
    print("Tables dropped successfully!")

    print("Creating all tables...")
    create_tables()
    print("Tables created successfully!")

    print("Importing data...")
    execute_sql_file('category_data.sql')
    print("Category data imported.")
    execute_sql_file('delivery_types_data.sql')
    print("Delivery types data imported.")
    execute_sql_file('shops_data.sql')
    print("Shops data imported.")
    execute_sql_file('payment_types_data.sql')
    print("Payment types data imported.")
    execute_sql_file('products_22082025.sql')
    print("Products data imported.")
    print("Data import complete!")

if __name__ == "__main__":
    reset_database()
    print("Database reset complete!")
