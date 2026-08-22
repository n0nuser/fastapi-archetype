from fastapi import APIRouter

from src.controller import api

router = APIRouter()
router.include_router(api.router)
