"""This module initializes the database."""

import logging

from sqlalchemy_utils import create_database, database_exists

from src.repository.models.base import Base
from src.repository.session import engine

logger = logging.getLogger(__name__)


def init_db() -> None:
    """Initialize the database."""
    # Creates database if it doesn't exist.
    if not database_exists(engine.url):
        logger.info("Creating database.")
        create_database(engine.url)
    with engine.begin() as conn:
        # Creates the tables if they don't exist.
        logger.info("Creating tables if they don't exist.")
        Base.metadata.create_all(bind=conn)

    # Create here the initial data to populate the database.
