import psycopg2

def execute_sql_file(filename):
    # Connect to the database
    conn = psycopg2.connect(
        dbname='ssms-db',
        user='postgres',
        password='postgres',
        host='localhost'
    )
    cur = conn.cursor()

    with open(filename, 'r') as f:
        cur.execute(f.read())

    conn.commit()
    cur.close()
    conn.close()

def run_sql_fix():
    print("Running Update...")
    execute_sql_file('fix_update0822.sql')
    print("Fix Update complete!")

if __name__ == "__main__":
    run_sql_fix()
    print("Database reset complete!")
