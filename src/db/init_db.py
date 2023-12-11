from src.db import crud
from src.api import 
from src.core.config import settings
from src.db.models.base import Base
from src.db.session import engine
from sqlalchemy_utils import create_database, database_exists


def init_db() -> None:
    # Creates database if it doesn't exist.
    if not database_exists(engine.url):
        create_database(engine.url)  # noqa: F821
    with engine.begin() as conn:
        # Creates the tables if they don't exist.
        Base.metadata.create_all(bind=conn)

    user = crud.CRUDUser.get_by_email(email=settings.FIRST_SUPERUSER)
    if not user:
        # Create user auth
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.CRUDUser.create(obj_in=user_in)  # noqa: F841
