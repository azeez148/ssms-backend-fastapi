import os

class Settings:
    # Email settings
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "adrenalinesportsstore44@gmail.com")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "oajy ubuh epgr dkrs")
    MAIL_FROM = os.getenv("MAIL_FROM", "adrenalinesportsstore44@gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_TLS = os.getenv("MAIL_TLS", "True").lower() in ("true", "1", "t")
    MAIL_SSL = os.getenv("MAIL_SSL", "False").lower() in ("true", "1", "t")

settings = Settings()
