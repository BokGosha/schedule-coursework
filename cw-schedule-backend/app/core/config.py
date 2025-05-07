from typing import Any, Dict, Optional

from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator
from functools import lru_cache
from app.core.logger import logger


class Settings(BaseSettings):
    PROJECT_NAME: str = "Schedule Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    USERNAME_MIN_LENGTH: int
    USERNAME_MAX_LENGTH: int
    PASSWORD_MIN_LENGTH: int

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=values.get("POSTGRES_DB") or "",
        ).unicode_string()

    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_database_url(self) -> str:
        return str(self.SQLALCHEMY_DATABASE_URI)

    def get_redis_url(self) -> str:
        return self.REDIS_URL


@lru_cache()
def get_settings() -> Settings:
    return Settings()
