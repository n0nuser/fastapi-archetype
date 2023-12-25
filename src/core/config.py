"""File with environment variables and general configuration logic.

`SECRET_KEY`, `ENVIRONMENT` etc. map to env variables with the same names.

Pydantic priority ordering:

1. (Most important, will overwrite everything) - environment variables
2. `.env` file in root folder of project
3. Default values

For project name, version, description we use pyproject.toml
For the rest, we use file `.env` (gitignored), see `.env.example`

`SQLALCHEMY_DATABASE_URI` is  meant to be validated at the runtime,
do not change unless you know what are you doing.
The validator is to build full URI (TCP protocol) to databases to avoid typo bugs.

See https://pydantic-docs.helpmanual.io/usage/settings/

Note, complex types like lists are read as json-encoded strings.
"""

import os
from typing import Any, Literal

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, validator
from pydantic_settings import BaseSettings

from src.core.logger import logger

load_dotenv()
logger.info(os.environ)


class Settings(BaseSettings):
    """Represents the configuration settings for the application."""

    # CORE SETTINGS
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "HDx09iYK97MzUqezQ8InThpcEBk791oi"
    ENVIRONMENT: Literal["DEV", "PYTEST", "PREPROD", "PROD"] = "PYTEST"
    SECURITY_BCRYPT_ROUNDS: int = 12
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # For example: '["http://localhost:4200", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1"]

    # POSTGRESQL DATABASE
    DATABASE_HOSTNAME: str = "db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "app-db"
    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    @classmethod
    def assemble_db_connection(cls: type["Settings"], v: str | None, values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    PROJECT_NAME: str = "{{cookiecutter.project_name}}"

    SMTP_TLS: bool = True
    SMTP_PORT: int | None = None
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None
    EMAILS_TO_EMAIL: EmailStr | None = None

    @validator("EMAILS_FROM_NAME")
    @classmethod
    def get_project_name(cls, v: str | None, values: dict[str, Any]) -> str:
        return v or values["PROJECT_NAME"]

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"
    EMAILS_ENABLED: bool = False

    @validator("EMAILS_ENABLED", pre=True)
    @classmethod
    def get_emails_enabled(cls, v: bool, values: dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST") and values.get("SMTP_PORT") and values.get("EMAILS_FROM_EMAIL"),
        )

    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    USERS_OPEN_REGISTRATION: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings: Settings = Settings()  # type: ignore
