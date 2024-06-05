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

import pathlib
from typing import Literal

from dotenv import load_dotenv
from pydantic import PostgresDsn, ValidationInfo, field_validator
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings

IS_ENV_FOUND = load_dotenv(dotenv_path=pathlib.Path(__file__).parent.parent / ".env")


class Settings(BaseSettings):
    """Represents the configuration settings for the application."""

    # CORE SETTINGS
    SECRET_KEY: str = "HDx09iYK97MzUqezQ8InThpcEBk791oi"
    ENVIRONMENT: Literal["DEV", "PYTEST", "PREPROD", "PROD"] = "DEV"
    ## BACKEND_CORS_ORIGINS and ALLOWED_HOSTS are a JSON-formatted list of origins
    ## For example: ["http://localhost:4200", "https://myfrontendapp.com"]
    BACKEND_CORS_ORIGINS: list[str] = []
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1"]
    APP_LOG_FILE_PATH: str = "logs/app.log"

    # POSTGRESQL DATABASE
    POSTGRES_SERVER: str = "db"  # The name of the service in the docker-compose file
    POSTGRES_USER: str = "postgres"  # The default username for the PostgreSQL database
    POSTGRES_PASSWORD: str = "postgres"  # The default password for the PostgreSQL database
    POSTGRES_PORT: int = 5432  # The default port for the PostgreSQL database
    POSTGRES_DB: str = "app-db"  # The default database name for the PostgreSQL database
    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None

    # CONNECTION POOL SETTINGS
    # The size of the pool to be maintained, defaults to 5
    POOL_SIZE: int = 10
    # Controls the number of connections that can be created after the pool reached its size
    MAX_OVERFLOW: int = 20
    # Number of seconds to wait before giving up on getting a connection from the pool
    POOL_TIMEOUT: int = 30
    # Number of seconds after which a connection is recycled (preventing stale connections)
    POOL_RECYCLE: int = 1800

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(
        cls: type["Settings"], v: str | None, info: ValidationInfo
    ) -> PostgresDsn:
        """Builds the database connection URI.

        Args:
            v (str | None): Value of the database connection URI.
            values (dict[str, Any]): Values of the database connection URI.
            info (ValidationInfo): Validation information.

        Returns:
            MultiHostUrl: The database connection URI.
        """
        if isinstance(v, str):
            return MultiHostUrl(v)
        return PostgresDsn.build(
            scheme="postgresql",
            username=info.data["POSTGRES_USER"],
            password=info.data["POSTGRES_PASSWORD"],
            host=info.data["POSTGRES_SERVER"],
            path=info.data["POSTGRES_DB"] or "",
        )

    # Additional Project Settings
    BASE_API_PATH: str
    API_VERSION: str
    PROJECT_NAME: str
    PROJECT_DESCRIPTION: str
    CONTACT_NAME: str
    CONTACT_EMAIL: str

    class Config:
        """Configuration for the settings class."""

        env_file = ".env"
        case_sensitive = True


settings: Settings = Settings()
