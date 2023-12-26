from fastapi import APIRouter

from src.api import api_v1
from src.core.config import settings

router = APIRouter()
router.include_router(api_v1.router, prefix=settings.API_V1_STR)
