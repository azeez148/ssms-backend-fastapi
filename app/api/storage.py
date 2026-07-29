from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from app.services.storage import StorageService
from app.api.auth import get_current_user_admin
from pydantic import BaseModel

router = APIRouter()
storage_service = StorageService()

@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    folder: str = "products",
    current_user = Depends(get_current_user_admin)
):
    """
    Upload an image to Cloudflare R2.
    """
    url = await storage_service.upload_image(file, folder)
    return {"url": url}

@router.delete("/upload-image")
async def delete_image(
    file_url: str = Query(...),
    current_user = Depends(get_current_user_admin)
):
    """
    Delete an image from Cloudflare R2.
    """
    await storage_service.delete_image(file_url)
    return {"message": "Image deletion requested"}
