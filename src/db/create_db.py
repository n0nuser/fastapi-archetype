from sqlalchemy_utils import create_database, database_exists

from src.api.schemas.user import UserCreate
from src.core.config import settings
from src.db.crud.crud_user import CRUDUser
from src.db.models.base import Base
from src.db.session import get_db_session


def init_db() -> None:
    """Initialize the database."""
    # Creates database if it doesn't exist.
    if not database_exists(engine.url):
        create_database(engine.url)
    with engine.begin() as conn:
        # Creates the tables if they don't exist.
        Base.metadata.create_all(bind=conn)

    crud_user = CRUDUser()
    with get_db_session() as db:
        user = crud_user.get_by_email(db=db, email=settings.FIRST_SUPERUSER)
        if not user:
            # Create user auth
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
            )
            user = crud_user.create(obj_in=user_in)
