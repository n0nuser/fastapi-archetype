import httpx
import pytest

from src.core import config
from src.db.models import Base
from src.db.session import engine
from src.tests.utils import REQUEST_HEADERS


@pytest.fixture(scope="session", autouse=True)
def test_db_setup_sessionmaker():
    # assert if we use TEST_DB URL for 100%
    assert config.settings.ENVIRONMENT == "PYTEST"

    # always drop and create test db tables between tests session
    with engine.begin() as conn:
        Base.metadata.drop_all(bind=conn)
        Base.metadata.create_all(bind=conn)


class MyHTTPXClient:
    def __init__(self, base_url: str, headers: dict = None):
        self.base_url = base_url
        self.headers = headers or REQUEST_HEADERS

    def request(
        self,
        method: str,
        url: str,
        headers: dict = None,
        params: dict = None,
        **kwargs,
    ):
        headers = headers or self.headers
        url = self.base_url + url

        with httpx.Client() as client:
            # response = client.request(method, url, headers=headers, params=params, **kwargs)
            # response.raise_for_status()
            # return response.json()
            return client.request(method, url, headers=headers, params=params, **kwargs)


@pytest.fixture()
def client() -> MyHTTPXClient:
    return MyHTTPXClient(base_url="http://localhost:8000/offices-system/v1")
