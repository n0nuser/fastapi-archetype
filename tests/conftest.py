"""Shared fixtures for the test suite.

Integration fixtures require a real Postgres instance:
    docker compose -f docker/docker-compose.test.yml up -d db-test
"""

import os

# Celery must resolve to non-network transports during tests; these are read
# by pydantic-settings when src.core.config is first imported.
os.environ.setdefault("CELERY_BROKER_URL", "memory://")
os.environ.setdefault("CELERY_RESULT_BACKEND", "cache+memory://")
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from src.app import app
from src.repository.models.base import Base
from src.repository.session import get_db_session

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5433/app_db_test",
)


@pytest.fixture(scope="session")
def test_engine() -> Iterator[Engine]:
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(test_engine: Engine) -> Iterator[Session]:
    """Session bound to an outer transaction; crud-level commits land in savepoints."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    """API client whose DB dependency is the isolated test session.

    No lifespan events: the app's init_db startup hook targets the runtime
    database, while the suite manages its own schema on the test engine.
    """

    def override_get_db_session() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    yield TestClient(app, base_url="http://localhost")
    app.dependency_overrides.clear()
