from imagekitio import ImageKit
from app.core.config import settings
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

class ImageKitService:
    def __init__(self):
        self.imagekit = ImageKit(
            private_key=settings.IMAGEKIT_PRIVATE_KEY,
            public_key=settings.IMAGEKIT_PUBLIC_KEY,
            url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
        )

    def upload_image(self, file, file_name):
        try:
            options = UploadFileRequestOptions(
                transformation={}
            )
            upload_info = self.imagekit.upload(
                file=file,
                file_name=file_name,
                options=options,
            )
            return upload_info.url
        except Exception as e:
            raise e
