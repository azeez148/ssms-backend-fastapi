import pytest
from unittest.mock import MagicMock, patch
from fastapi import UploadFile
from app.services.storage import StorageService
import io

@pytest.fixture
def storage_service():
    with patch('boto3.client'):
        # Mock settings to have required R2 credentials
        with patch('app.services.storage.settings') as mock_settings:
            mock_settings.R2_ACCOUNT_ID = "test-account"
            mock_settings.R2_ACCESS_KEY_ID = "test-key"
            mock_settings.R2_SECRET_ACCESS_KEY = "test-secret"
            mock_settings.R2_BUCKET_NAME = "test-bucket"
            mock_settings.R2_PUBLIC_URL = "https://cdn.example.com"
            yield StorageService()

@pytest.mark.asyncio
async def test_generate_unique_filename(storage_service):
    filename = "test.jpg"
    unique_name = storage_service.generate_unique_filename(filename)
    assert unique_name.endswith(".jpg")
    assert len(unique_name) > 10

@pytest.mark.asyncio
@patch('app.services.storage.run_in_threadpool')
async def test_upload_image_success(mock_run, storage_service):
    # Mock content type check and put_object
    async def side_effect(func, *args, **kwargs):
        if func == storage_service._get_content_type:
            return "image/jpeg"
        return None

    mock_run.side_effect = side_effect

    # Mock UploadFile
    content = b"fake image content"
    file = MagicMock(spec=UploadFile)
    file.filename = "test.jpg"
    file.read.return_value = content

    url = await storage_service.upload_image(file)

    assert url.startswith("https://cdn.example.com/products/")
    assert url.endswith(".jpg")
    assert mock_run.call_count == 2 # 1 for content type, 1 for put_object

@pytest.mark.asyncio
@patch('app.services.storage.run_in_threadpool')
async def test_upload_image_invalid_type(mock_run, storage_service):
    mock_run.return_value = "application/pdf"

    file = MagicMock(spec=UploadFile)
    file.filename = "test.pdf"
    file.read.return_value = b"fake pdf content"

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as excinfo:
        await storage_service.upload_image(file)

    assert excinfo.value.status_code == 400
    assert "Unsupported file type" in excinfo.value.detail

@pytest.mark.asyncio
@patch('app.services.storage.run_in_threadpool')
async def test_delete_image(mock_run, storage_service):
    file_url = "https://cdn.example.com/products/test-uuid.jpg"

    await storage_service.delete_image(file_url)

    mock_run.assert_called_once()
    func_called = mock_run.call_args[0][0]
    args_called = mock_run.call_args[0][1:]
    assert func_called == storage_service._delete_object
    assert args_called == ("products/test-uuid.jpg",)
