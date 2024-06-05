"""Database session management."""

import logging
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from src.core.config import settings

logger = logging.getLogger(__name__)

# Create a new engine with connection pooling
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_pre_ping=True,
    poolclass=QueuePool,
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
    pool_timeout=settings.POOL_TIMEOUT,
    pool_recycle=settings.POOL_RECYCLE,
)

# Create a session factory
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Iterator[Session]:
    """Get a SQLAlchemy database session.

    Yields:
        Generator[Session, None, None]: A SQLAlchemy database session.

    Example:
        Usage in a FastAPI route:

        ```python
        @app.get("/example/")
        async def example_route(db: Session = Depends(get_db_session)):
            # Your route logic here
            pass
        ```
    """
    # Create a new session
    logger.debug("Creating a new session.")
    session = session_local()
    try:
        logger.debug("Yielding the session.")
        yield session
    finally:
        logger.debug("Closing the session.")
        session.close()
