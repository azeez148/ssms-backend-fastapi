from app.core.database import Base, engine
from app.models import *  # This will import all models
from sqlalchemy import text

def create_tables():
    # Drop schema with CASCADE to handle dependencies
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
        conn.commit()
    
    # Create all tables fresh
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("Tables created successfully!")
