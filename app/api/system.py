from fastapi import APIRouter
import sys
import os

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from reset_db import reset_database

router = APIRouter()

@router.post("/reset-db", tags=["system"])
async def reset_db_endpoint():
    """
    Resets the entire database by dropping all tables, recreating them, and seeding initial data.
    """
    try:
        reset_database()
        return {"message": "Database reset successfully!"}
    except Exception as e:
        return {"message": f"An error occurred during database reset: {e}"}
