from src.db.crud.base import CRUDBase
from src.db.models.customer import Customer


class CRUDCustomer(CRUDBase[Customer]):
    pass


customer_crud = CRUDCustomer(Customer)
