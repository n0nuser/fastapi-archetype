from fastapi import APIRouter

from src.controller.api.endpoints import customer

router = APIRouter()
router.include_router(customer.router)
