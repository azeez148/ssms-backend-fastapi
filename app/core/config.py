import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Email settings
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "adrenalinesportsstore44@gmail.com")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "oajy ubuh epgr dkrs")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "adrenalinesportsstore44@gmail.com")
    MAIL_PORT: int = 587
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    SYSTEM_PASS_KEY: str = os.getenv("SYSTEM_PASS_KEY", "7736")

    class Config:
        env_file = ".env"
        extra = 'ignore'

settings = Settings()
