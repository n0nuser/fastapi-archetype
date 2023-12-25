"""Database session management."""
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.core.config import settings

# Create a new engine
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), pool_pre_ping=True)

# Create a session factory
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager()
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
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
