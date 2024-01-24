from src.repository.crud.base import CRUDBase
from src.repository.models.customer import Address


class CRUDAddress(CRUDBase[Address]):
    pass


address_crud = CRUDAddress(Address)
