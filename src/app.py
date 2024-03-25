"""Main FastAPI app instance declaration."""

from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from src.controller import router
from src.controller.errors.exception_manager import manage_api_exceptions
from src.core.config import settings
from src.core.logger import logger
from src.repository.create_db import init_db
from src.repository.session import get_db_session

root_path = f"/api/{settings.BASE_API_PATH}"

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{root_path}/openapi.json",
    version=settings.API_VERSION,
    description=settings.PROJECT_DESCRIPTION,
    contact={
        "name": settings.CONTACT_NAME,
        "email": settings.CONTACT_EMAIL,
    },
    docs_url=f"{root_path}/swagger",
    on_startup=[init_db],
    on_shutdown=[],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

app.include_router(router, prefix=root_path)


@app.get(
    "/health-check",
    tags=["Health Check"],
    response_model=dict[str, str],
    summary="Health Check Endpoint",
    description="Endpoint to check the status of the application.",
)
async def health_check(
    db_connection: Annotated[Session, Depends(get_db_session)],
) -> dict[str, str]:
    """Health check endpoint that now includes database connectivity check.

    Attempts to make a simple query to the database to ensure connectivity.

    Returns:
        dict[str, str]: A dictionary with the status of the application and database connectivity.
    """
    try:
        # Attempt a simple query to check database connectivity
        # The specific query can be adjusted based on your database schema.
        # Here, we're just checking if we can execute a simple SELECT.
        db_connection.execute("SELECT 1")
    except OperationalError:
        # If database connection fails, catch the error and return an appropriate response
        return {"status": "error", "database": "disconnected"}
    else:
        return {"status": "ok", "database": "connected"}


manage_api_exceptions(app=app)
logger.debug(app.routes)
