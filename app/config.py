from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None
    DATABASE_URL: str
    REDIS_URL: str | None = None

    ENV: str = "dev"

    model_config = SettingsConfigDict(env_file=BASE_DIR / "project.env", extra="ignore")


settings = Settings()
