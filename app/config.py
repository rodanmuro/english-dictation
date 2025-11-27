"""
Application configuration settings.
Loads environment variables from .env file.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Deepgram API configuration
    deepgram_api_key: str

    # File storage paths
    audio_dir: str = "app/static/audios"

    # Application settings
    app_name: str = "English Dictation App"
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()