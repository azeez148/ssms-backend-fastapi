from fastapi import APIRouter, HTTPException, status
import sys
import os
from pydantic import BaseModel

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from reset_db import reset_database
from app.core.config import settings

router = APIRouter()

class PassKey(BaseModel):
    pass_key: str

@router.post("/reset-db", tags=["system"])
async def reset_db_endpoint(item: PassKey):
    """
    Resets the entire database by dropping all tables, recreating them, and seeding initial data.
    """
    if item.pass_key != settings.SYSTEM_PASS_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid pass_key",
        )
    try:
        reset_database()
        return {"message": "Database reset successfully!"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during database reset: {e}"
        )

@router.post("/backup-db", tags=["system"])
async def backup_db_endpoint(item: PassKey):
    """
    Creates a backup of the database.
    Requires a valid pass_key.
    """
    if item.pass_key != settings.SYSTEM_PASS_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid pass_key",
        )
    # Placeholder for backup logic
    return {"message": "Backup functionality not implemented yet."}

@router.post("/restore-db", tags=["system"])
async def restore_db_endpoint(item: PassKey):
    """
    Restores the database from a backup.
    Requires a valid pass_key.
    """
    if item.pass_key != settings.SYSTEM_PASS_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid pass_key",
        )
    # Placeholder for restore logic
    return {"message": "Restore functionality not implemented yet."}
