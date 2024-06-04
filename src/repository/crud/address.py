"""CRUD operations for the Address model."""

from src.repository.crud.base import CRUDBase
from src.repository.models.customer import Address


class CRUDAddress(CRUDBase[Address]):
    """CRUD operations for the Address model."""


address_crud = CRUDAddress(Address)
