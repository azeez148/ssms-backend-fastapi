from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# SQLite Database URL
# PostgreSQL Database URL
POSTGRES_USER = os.getenv("POSTGRES_USER", "ssms_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "an5OnVThslPXYeT86hqqflGiWlBXHz06")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "postgresql://ssms_user:an5OnVThslPXYeT86hqqflGiWlBXHz06@dpg-d29jmangi27c73cm32ug-a/ssms")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "ssms")

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
