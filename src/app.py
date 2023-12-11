"""Main FastAPI app instance declaration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.api import ApiRouter
from src.api.endpoints.createdb import router as DBRouter
from src.api.responses.exception_manager import manage_api_exceptions
from src.core import config
from src.db.init_db import init_db

ACCEPT_LANGUAGE_REGEX = r"^[a-z]{2}-[A-Z]{2}$"
X_REQUEST_ID_REGEX = (
    r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$"
)


def create_app() -> FastAPI:
    """Returns a FastAPI app.

    Returns:
        FastAPI: FastAPI application.
    """
    port = 8000
    base_path = "offices-system"
    major_version = "v1"
    root_path = f"/{base_path}/{major_version}"

    app = FastAPI(
        title="Offices System",
        version="1.0.0",
        description="This API allows you to manage the reservations of the sites within the office.",
        contact={"name": "Alberto Iglesias", "email": "aiglesiass@axpe.com"},
        servers=[
            {
                "url": "{protocol}://{host}:{port}/{basePath}/{MajorVersion}",
                "variables": {
                    "protocol": {"description": "Protocol.", "default": "http"},
                    "host": {"description": "Host.", "default": "0.0.0.0"},
                    "port": {"description": "Port.", "default": port},
                    "basePath": {"description": "BasePath.", "default": base_path},
                    "MajorVersion": {
                        "description": "MajorVersion.",
                        "default": major_version,
                    },
                },
            }
        ],
        openapi_url="/openapi.json",
        docs_url=root_path,
        on_startup=[startup],
        on_shutdown=[shutdown],
    )

    init_routers(app=app, root_path=root_path)
    init_cors(app=app)
    init_security(app=app)
    manage_api_exceptions(app=app)

    return app


async def startup():
    """Function to run at FastAPI Startup"""
    init_db()


async def shutdown():
    """Function to run at FastAPI Shutdown"""


def init_cors(app: FastAPI) -> None:
    """Initialize CORS in the FastAPI app.

    Args:
        app (FastAPI): FastAPI application.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in config.settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def init_security(app: FastAPI) -> None:
    # Guards against HTTP Host Header attacks
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=config.settings.ALLOWED_HOSTS
    )


def init_routers(app: FastAPI, root_path: str) -> None:
    """Set routers for the FastAPI app.

    Args:
        app (FastAPI): FastAPI application.
    """
    if config.settings.ENVIRONMENT in ["PYTEST", "DEV"]:
        app.include_router(DBRouter, prefix=root_path)
    app.include_router(ApiRouter, prefix=root_path)


app = create_app()
