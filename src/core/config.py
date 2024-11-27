import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    DEBUG: bool = False

    ACCESS_TOKEN_EXPIRY_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRY_MINUTES", 60))
    REFRESH_TOKEN_EXPIRY_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRY_DAYS", 2))

    DATABASE_URL: str
    REDIS_URL: str
    # Celery Configuration
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    # Mail Configuration (SMTP)
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_SERVER: str
    MAIL_HOST: str
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    MAIL_FROM: str
    MAIL_FROM_NAME: str
    MAIL_TLS: bool = bool(int(os.getenv("MAIL_TLS", 1)))
    MAIL_SSL: bool = bool(int(os.getenv("MAIL_SSL", 0)))

    JWT_SECRET: str
    JWT_ALGORITHM: str

    INSTAGRAM_APP_SECRET: str
    INSTAGRAM_APP_ID: str
    INSTAGRAM_APP_NAME: str
    INSTAGRAM_REDIRECT_URI: str


    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Use the settings class for the app config
Config = Settings()