"""Main FastAPI app instance declaration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.api import router
from src.api.errors.exception_manager import manage_api_exceptions
from src.core.config import settings
from src.db.create_db import init_db

ACCEPT_LANGUAGE_REGEX = r"^[a-z]{2}-[A-Z]{2}$"
X_REQUEST_ID_REGEX = (
    r"^[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}$"
)
port = 8000
base_path = "offices-system"
major_version = "v1"
root_path = f"/{base_path}/{major_version}"

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="1.0.0",
    description="{{cookiecutter.project_description}}",
    contact={
        "name": "{{cookiecutter.author_name}}",
        "email": "{{cookiecutter.author_email}}",
    },
    docs_url=root_path,
    on_startup=[init_db],
    on_shutdown=[],
)

app.include_router(router, prefix=root_path)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
manage_api_exceptions(app=app)
