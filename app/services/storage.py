import boto3
import uuid
import magic
import os
from botocore.config import Config
from fastapi import UploadFile, HTTPException
from starlette.concurrency import run_in_threadpool
from typing import Optional, List
from app.core.config import settings
from app.core.logging import logger

class StorageService:
    def __init__(self):
        self.s3_client = None
        if all([settings.R2_ACCOUNT_ID, settings.R2_ACCESS_KEY_ID, settings.R2_SECRET_ACCESS_KEY]):
            self.s3_client = boto3.client(
                service_name="s3",
                endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
                aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                config=Config(signature_version="s3v4"),
                region_name="auto"
            )
        else:
            logger.warning("Cloudflare R2 credentials not fully configured. StorageService might not work correctly.")

        self.bucket_name = settings.R2_BUCKET_NAME
        self.public_url = settings.R2_PUBLIC_URL.rstrip("/")
        self.allowed_content_types = ["image/jpeg", "image/png", "image/webp"]
        self.max_file_size = 5 * 1024 * 1024  # 5MB

    def generate_unique_filename(self, original_filename: str) -> str:
        ext = os.path.splitext(original_filename)[1].lower()
        return f"{uuid.uuid4()}{ext}"

    def _get_content_type(self, content: bytes) -> str:
        return magic.from_buffer(content, mime=True)

    def _put_object(self, object_key: str, content: bytes, content_type: str):
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=object_key,
            Body=content,
            ContentType=content_type
        )

    def _delete_object(self, object_key: str):
        self.s3_client.delete_object(
            Bucket=self.bucket_name,
            Key=object_key
        )

    async def upload_image(self, file: UploadFile, folder: str = "products") -> str:
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="Storage service not configured")

        # Read file content
        content = await file.read()
        file_size = len(content)

        # Validate file size
        if file_size > self.max_file_size:
            raise HTTPException(status_code=400, detail=f"File size exceeds limit of {self.max_file_size // (1024*1024)}MB")

        # Validate content type (running in threadpool as magic can be slow)
        content_type = await run_in_threadpool(self._get_content_type, content)
        if content_type not in self.allowed_content_types:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}. Allowed: {', '.join(self.allowed_content_types)}")

        # Generate unique filename
        filename = self.generate_unique_filename(file.filename)
        object_key = f"{folder}/{filename}"

        try:
            # Upload to R2 (running in threadpool as boto3 is blocking)
            await run_in_threadpool(self._put_object, object_key, content, content_type)

            return f"{object_key}"

        except Exception as e:
            logger.error(f"Error uploading image to R2: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Could not upload image: {str(e)}")

    async def delete_image(self, file_url: str):
        if not self.s3_client:
            logger.warning("Storage service not configured, skipping deletion.")
            return

        try:
            # Extract object key from URL
            if self.public_url and file_url.startswith(self.public_url):
                object_key = file_url.replace(f"{self.public_url}/", "")
            else:
                parts = file_url.split("/")
                object_key = "/".join(parts[-2:])

            await run_in_threadpool(self._delete_object, object_key)
            logger.info(f"Deleted image from R2: {object_key}")
        except Exception as e:
            logger.error(f"Error deleting image from R2: {str(e)}")
