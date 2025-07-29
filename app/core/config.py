import os

class Settings:
    # Email settings
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "your-email@example.com")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "your-password")
    MAIL_FROM = os.getenv("MAIL_FROM", "your-email@example.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.example.com")
    MAIL_TLS = os.getenv("MAIL_TLS", "True").lower() in ("true", "1", "t")
    MAIL_SSL = os.getenv("MAIL_SSL", "False").lower() in ("true", "1", "t")

settings = Settings()
