from src.db.crud.base import CRUDBase
from src.db.models.customer import Address


class CRUDAddress(CRUDBase[Address]):
    pass


address_crud = CRUDAddress(Address)
