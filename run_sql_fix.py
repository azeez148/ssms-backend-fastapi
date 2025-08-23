from sqlalchemy import text
from app.core import database
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_sql_fix():
    """
    Connects to the database using the app's shared SQLAlchemy engine
    and executes the SQL commands from fix_update0822.sql.
    """
    logging.info("Starting the SQL fix script...")
    try:
        # --- Read SQL File ---
        sql_file_path = 'fix_update0822.sql'
        logging.info(f"Reading SQL file: {sql_file_path}")
        with open(sql_file_path, 'r') as f:
            sql_commands = f.read()

        # --- Connect and Execute ---
        logging.info("Connecting to the database using the application's engine...")
        with database.engine.connect() as connection:
            logging.info("Connection successful. Executing SQL commands...")

            # The `with database.engine.connect()` block manages the connection
            # and transaction. A transaction is started on first execute, and is
            # automatically committed if the block succeeds, or rolled back on error.
            connection.execute(text(sql_commands))

            logging.info("SQL script 'fix_update0822.sql' executed successfully!")
            logging.info("The category_id for the specified products has been updated.")

    except FileNotFoundError:
        logging.error(f"Error: The file '{sql_file_path}' was not found.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    run_sql_fix()
    logging.info("Script finished.")
