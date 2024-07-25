from functools import lru_cache
from typing import Optional, Any
import os

from pydantic import PostgresDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DOTENV = os.path.join(os.path.dirname(__file__), ".env")


class Settings(BaseSettings):
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str
    MINIO_EDNPOINT: str
    MINIO_HOST: str

    class Config:
        env_file='.env'
        extra='ignore'


@lru_cache
def get_settings():
    return Settings()

settings = get_settings()