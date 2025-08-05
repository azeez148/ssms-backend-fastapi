import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Email settings
    MAIL_USERNAME: str = "adrenalinesportsstore44@gmail.com"
    MAIL_PASSWORD: str = "oajy ubuh epgr dkrs"
    MAIL_FROM: str = "adrenalinesportsstore44@gmail.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False

    # ImageKit.io settings
    IMAGEKIT_PRIVATE_KEY: Optional[str] = None
    IMAGEKIT_PUBLIC_KEY: Optional[str] = None
    IMAGEKIT_URL_ENDPOINT: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = 'ignore'

settings = Settings()
