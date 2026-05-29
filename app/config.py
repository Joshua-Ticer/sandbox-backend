from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / "project.env"
    )

settings = Settings()

