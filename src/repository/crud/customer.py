"""CRUD operations for the Customer model."""

from src.repository.crud.base import CRUDBase
from src.repository.models.customer import Customer


class CRUDCustomer(CRUDBase[Customer]):
    """CRUD operations for the Customer model."""


customer_crud = CRUDCustomer(Customer)
