"""Main FastAPI app instance declaration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.api import router
from src.api.errors.exception_manager import manage_api_exceptions
from src.core.config import settings
from src.core.logger import logger
from src.db.create_db import init_db

root_path = f"/api/{settings.BASE_API_PATH}"

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{root_path}/openapi.json",
    version="1.0.0",
    description=settings.PROJECT_DESCRIPTION,
    contact={
        "name": settings.CONTACT_NAME,
        "email": settings.CONTACT_EMAIL,
    },
    docs_url=f"{root_path}/swagger",
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
logger.debug(app.routes)
