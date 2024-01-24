from src.repository.crud.base import CRUDBase
from src.repository.models.customer import Customer


class CRUDCustomer(CRUDBase[Customer]):
    pass


customer_crud = CRUDCustomer(Customer)
