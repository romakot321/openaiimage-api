from typing import Literal
from pydantic import AnyUrl, PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    LOCAL_STORAGE_PATH: str = "storage"
    ENVIRONMENT: Literal['test', 'prod'] = 'prod'
    DOMAIN: str
    API_TOKEN: str = "123"

    PROJECT_NAME: str = os.environ.get("PROJECT_NAME", "UNNAMED PROJECT")

    REDIS_HOST: str

    DB_TYPE: Literal['POSTGRESQL', 'ASYNC_POSTGRESQL', 'SQLITE', 'ASYNC_SQLITE'] = os.environ.get("DB_TYPE")
    DB_NAME: str = os.environ.get("DB_NAME")
    DB_USER: str | None = os.environ.get("DB_USER")
    DB_PASSWORD: str | None = os.environ.get("DB_PASSWORD")
    DB_HOST: str | None = os.environ.get("DB_HOST")
    DB_PORT: str | None = os.environ.get("DB_PORT")
    DATABASE_URI: str | None = None
    ALEMBIC_DATABASE_URI: str | None = None

    CONTEXT_MAX_SYMBOLS: int = 30000
    CONTEXT_MAX_IMAGES: int = 16

    @staticmethod
    def _build_dsn(scheme: str, values: dict) -> str:
        return str(
            PostgresDsn.build(
                scheme=scheme,
                username=values.get("DB_USER"),
                password=values.get("DB_PASSWORD"),
                host=values.get("DB_HOST"),
                port=int(values["DB_PORT"]) if values.get("DB_PORT") else None,
                path=values.get("DB_NAME"),
            )
        )

    @field_validator("API_TOKEN")
    def validate_api_token(cls, v: str, info: ValidationInfo) -> str:
        if v == "123" and info.data.get("ENVIRONMENT") == "prod":
            raise ValueError("Define not default api_token env")
        return v

    @field_validator("DATABASE_URI")
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if isinstance(v, str):
            return v
        elif isinstance(v, AnyUrl):
            return str(v)
        db_type = info.data.get("DB_TYPE")
        if db_type == "ASYNC_SQLITE":
            return "sqlite+aiosqlite:///:memory:"
        elif db_type == "POSTGRESQL":
            return cls._build_dsn("postgresql+psycopg", info.data)
        elif db_type == "ASYNC_POSTGRESQL":
            return cls._build_dsn("postgresql+asyncpg", info.data)
        raise ValueError("Unsupported database type")

    @field_validator("ALEMBIC_DATABASE_URI", mode="before")
    def assemble_alembic_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if isinstance(v, str):
            return v
        elif isinstance(v, AnyUrl):
            return str(v)
        return info.data.get("DATABASE_URI")


settings = Settings()
