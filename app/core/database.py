from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


# Database configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "ssms_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "an5OnVThslPXYeT86hqqflGiWlBXHz06")
# ✅ This should ONLY be the hostname
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "dpg-d29jmangi27c73cm32ug-a")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "ssms")

# This line now works correctly because the components are correct
SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
