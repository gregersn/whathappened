"""App default config."""
import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings to be overridden with env variables."""

    ADMINS: List[str] = ["your-email@example.com"]
    ASSETS_DEBUG: bool = False
    FLASK_DEBUG: bool = True
    MAIL_PORT: int = 8025
    MAIL_SERVER: str = "localhost"
    MAX_CONTENT_LENGTH: int = 1024 * 1024  # Max upload size
    SECRET_KEY: str = "development"
    SQLALCHEMY_DATABASE_URI: Optional[str] = (
        os.environ.get("DATABASE_URL")
        or f"sqlite:///{Path(__file__).parent.parent / 'instance' / 'whathappened.sqlite'}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    UPLOAD_EXTENSIONS: List[str] = [".jpg", ".png", ".jpeg", ".gif"]
    UPLOAD_FOLDER: str = "uploads"
    WEBPACKEXT_MANIFEST_PATH: str = "manifest.json"
    WTF_CSRF_TIME_LIMIT: Optional[int] = None

    class Config:
        _env_file_encoding = "utf-8"


Config = Settings(_env_file=os.environ.get("WHATHAPPENED_SETTINGS"))

if __name__ == "__main__":  # pragma: no cover
    print(Config)
