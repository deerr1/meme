from functools import lru_cache
from typing import Optional, Any
import os

from pydantic import PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_IMAGE_ROUTE: str
    STORAGE_USERNAME: str
    STORAGE_PASSWORD: str
    STORAGE_ENDPOINT: str
    STORAGE_GET_ROUTE: str
    STORAGE_PUT_ROUTE: str
    STORAGE_DELETE_ROUTE: str
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: PostgresDsn | str = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"{values.get('POSTGRES_DB') or ''}",
        ).unicode_string()

    class Config:
        env_file='.env'
        extra='ignore'


@lru_cache
def get_settings():
    return Settings()

settings = get_settings()