from fastapi import status
from requests import Response

from src.api.responses.error_responses import ERROR_RESPONSES

REQUEST_HEADERS = {
    "Accept-Language": "en-EN",
    "X-Request-ID": "54b9c11c-9162-45a1-a352-0d95734cd079",
    # "Authorization": "Bearer special-key",
}


def assert_400(response: Response):
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert str(response.json()) == str(ERROR_RESPONSES.get(400).dict())
    assert "X-Request-ID" in response.headers


def assert_404(response: Response):
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert str(response.json()) == str(ERROR_RESPONSES.get(404).dict())
    assert "X-Request-ID" in response.headers


def assert_204(response: Response):
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert "X-Request-ID" in response.headers


def assert_201(response: Response):
    assert response.status_code == status.HTTP_201_CREATED
    assert "X-Request-ID" in response.headers
    # TODO
    # assert "Location" in response.headers
