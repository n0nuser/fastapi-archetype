from fastapi import APIRouter

from src.api.api_v1.endpoints import customer

router = APIRouter()
router.include_router(customer.router)
