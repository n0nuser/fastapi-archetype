"""
File with environment variables and general configuration logic.
`SECRET_KEY`, `ENVIRONMENT` etc. map to env variables with the same names.

Pydantic priority ordering:

1. (Most important, will overwrite everything) - environment variables
2. `.env` file in root folder of project
3. Default values

For project name, version, description we use pyproject.toml
For the rest, we use file `.env` (gitignored), see `.env.example`

`DEFAULT_SQLALCHEMY_DATABASE_URI` is  meant to be validated at the runtime, 
do not change unless you know what are you doing. 
All the two validators do is to build full URI (TCP protocol)
to databases to avoid typo bugs.

See https://pydantic-docs.helpmanual.io/usage/settings/

Note, complex types like lists are read as json-encoded strings.
"""

import os
from typing import Any, Dict, Literal, Optional

from dotenv import load_dotenv
from pydantic import PostgresDsn, validator, EmailStr
from pydantic_settings import BaseSettings


from src.core.logger import logger

load_dotenv()
logger.info(os.environ)


class Settings(BaseSettings):
    # CORE SETTINGS
    SECRET_KEY: str = "HDx09iYK97MzUqezQ8InThpcEBk791oi"
    ENVIRONMENT: Literal["DEV", "PYTEST", "PREPROD", "PROD"] = "PYTEST"
    SECURITY_BCRYPT_ROUNDS: int = 12
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1"]

    # POSTGRESQL DATABASE
    DATABASE_HOSTNAME: str = "db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "app-db"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    EMAILS_TO_EMAIL: Optional[EmailStr] = None

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"
    EMAILS_ENABLED: bool = False

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    USERS_OPEN_REGISTRATION: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings: Settings = Settings()  # type: ignore
