from fastapi import APIRouter

from src.api.api_v1.endpoints import createdb
from src.core.config import settings

router = APIRouter()
if settings.ENVIRONMENT in ["PYTEST", "DEV"]:
    router.include_router(createdb.router)
