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
    ADMIN_PHONE_NUMBER: str = os.getenv("ADMIN_PHONE_NUMBER", "+917736994429")

    # Github settings
    GITHUB_REPO_URL: Optional[str] = os.getenv("GITHUB_REPO_URL", "https://github.com/adrenalines-sports/ssms-db-backup.git")
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN", None)

    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-here-for-jwt-tokens-keep-it-safe")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days


    class Config:
        env_file = ".env"
        extra = 'ignore'

settings = Settings()
