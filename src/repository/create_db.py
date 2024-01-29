"""This module initializes the database."""

from sqlalchemy_utils import create_database, database_exists

from src.repository.models.base import Base
from src.repository.session import engine


def init_db() -> None:
    """Initialize the database."""
    # Creates database if it doesn't exist.
    if not database_exists(engine.url):
        create_database(engine.url)
    with engine.begin() as conn:
        # Creates the tables if they don't exist.
        Base.metadata.create_all(bind=conn)

    # Create here the initial data to populate the database.
