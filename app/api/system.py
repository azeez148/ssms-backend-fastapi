from fastapi import APIRouter, HTTPException, status
import sys
import os
from pydantic import BaseModel
import subprocess
import datetime
from app.core.database import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_SERVER

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from reset_db import reset_database
from app.core.config import settings
from run_new_sql_migration import run_sql_migrations

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
    Creates a backup of the database and uploads it to a GitHub repository.
    Requires a valid pass_key.
    """
    if item.pass_key != settings.SYSTEM_PASS_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid pass_key",
        )

    try:
        # --- Database Backup ---
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_file = os.path.join(backup_dir, f"backup_{timestamp}.sql")

        pg_dump_cmd = [
            "pg_dump",
            "-h", POSTGRES_SERVER,
            "-U", POSTGRES_USER,
            "-d", POSTGRES_DB,
            "-f", backup_file
        ]

        env = os.environ.copy()
        env["PGPASSWORD"] = POSTGRES_PASSWORD

        subprocess.run(pg_dump_cmd, check=True, env=env)

        # --- GitHub Upload ---
        repo_url = settings.GITHUB_REPO_URL
        token = settings.GITHUB_TOKEN

        repo_name = repo_url.split("/")[-1].replace(".git", "")
        repo_dir = os.path.join(backup_dir, repo_name)

        if not os.path.exists(repo_dir):
            clone_url = repo_url.replace("https://", f"https://{token}@")
            subprocess.run(["git", "clone", clone_url, repo_dir], check=True)

        backup_filename = os.path.basename(backup_file)
        new_backup_path = os.path.join(repo_dir, backup_filename)
        os.rename(backup_file, new_backup_path)

        subprocess.run(["git", "-C", repo_dir, "add", new_backup_path], check=True)
        subprocess.run(["git", "-C", repo_dir, "commit", "-m", f"Add backup {timestamp}"], check=True)
        subprocess.run(["git", "-C", repo_dir, "push"], check=True)

        return {"message": f"Backup created and uploaded successfully: {backup_filename}"}

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during the backup process: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )

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


# @router.post("/run-sql-fix", tags=["system"])
# async def run_sql_fix_endpoint(item: PassKey):
#     """
#     Executes the SQL fix script.
#     Requires a valid pass_key.
#     """
#     if item.pass_key != settings.SYSTEM_PASS_KEY:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid pass_key",
#         )
#     try:
#         run_sql_fix()
#         return {"message": "SQL fix script executed successfully!"}
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred during SQL fix execution: {e}"
#         )


@router.post("/run-sql-migrations", tags=["system"])
async def run_sql_migrations_endpoint(item: PassKey):
    """
    Executes the SQL fix script.
    Requires a valid pass_key.
    """
    if item.pass_key != settings.SYSTEM_PASS_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid pass_key",
        )
    try:
        run_sql_migrations()
        return {"message": "SQL script executed successfully!"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during SQL execution: {e}"
        )
