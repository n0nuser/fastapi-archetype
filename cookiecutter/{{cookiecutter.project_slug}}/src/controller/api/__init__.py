from fastapi import APIRouter

from src.controller.api.endpoints import customer
from src.controller.api.security import router as security_router

router = APIRouter()
router.include_router(customer.router)
router.include_router(security_router)
