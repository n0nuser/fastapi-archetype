import pytest
from fastapi import status
from requests import Response

from src.api.schemas.office_data import OfficeData
from src.api.schemas.office_data_data import OfficeDataData
from src.api.schemas.office_response import OfficeResponse
from src.api.schemas.office_response_data_inner import OfficeResponseDataInner
from src.api.schemas.pagination import Pagination
from src.tests.conftest import MyHTTPXClient
from src.tests.utils import (REQUEST_HEADERS, assert_201, assert_204,
                             assert_400, assert_404)


def assert_200_office(response: Response):
    assert response.status_code == status.HTTP_200_OK
    office_response = OfficeResponse.parse_obj(response.json())
    assert isinstance(office_response, OfficeResponse)
    assert isinstance(office_response.data[0], OfficeResponseDataInner)
    assert isinstance(office_response.pagination, Pagination)


def assert_200_office_id(response: Response):
    assert response.status_code == status.HTTP_200_OK
    office_response = OfficeData.parse_obj(response.json())
    assert isinstance(office_response, OfficeData)
    assert isinstance(office_response.data, OfficeDataData)


@pytest.mark.order(2)
def test_get_offices(client: MyHTTPXClient):
    """Test case for get_offices

    List of offices.
    """
    kwargs = {
        "method": "GET",
        "url": "/offices",
        "headers": REQUEST_HEADERS,
        "params": [("limit", 10), ("offset", 0), ("address_province", "address_province_example")],
    }
    response = client.request(**kwargs)
    assert_404(response)

    kwargs["params"] = [("limit", 10), ("offset", 0)]
    response = client.request(**kwargs)
    assert_200_office(response)


@pytest.mark.order(4)
def test_get_offices_office_id(client: MyHTTPXClient):
    """Test case for get_offices_office_id

    Office information.
    """
    kwargs = {
        "method": "GET",
        "url": f"/offices/{56}",
        "headers": REQUEST_HEADERS,
    }
    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = f"/offices/{1}"
    response = client.request(**kwargs)
    assert_200_office_id(response)


@pytest.mark.order(1)
def test_post_offices(client: MyHTTPXClient):
    """Test case for post_offices

    Create a new office.
    """
    kwargs = {
        "method": "POST",
        "url": "/offices",
        "headers": REQUEST_HEADERS,
        "json": {
            "data": {
                "name": "UXCALE POST",
                "line": "C/Toro, nº71",
                "streetName": "C/Toro",
                "buildingNumber": "nº 71",
                "stair": "1",
                "floor": 1,
                "doorNumber": "1A",
                "postalCode": "37002",
                "province": "Salamanca",
                "country": "ES",
            },
        },
    }

    response = client.request(**kwargs)
    assert_400(response)

    kwargs["json"] = {
        "name": "UXCALE POST",
        "line": "C/Toro, nº71",
        "streetName": "C/Toro",
        "buildingNumber": "nº 71",
        "stair": "1",
        "floor": 1,
        "doorNumber": "1A",
        "postalCode": "37002",
        "province": "Salamanca",
        "country": "ES",
    }
    response = client.request(**kwargs)
    assert_201(response)


@pytest.mark.order(3)
def test_put_offices_office_id(client: MyHTTPXClient):
    """Test case for put_offices_office_id

    Update information from a office.
    """
    kwargs = {
        "method": "PUT",
        "url": f"/offices/{56}",
        "headers": REQUEST_HEADERS,
        "json": {
            "data": {
                "name": "UXCALE PUT",
                "line": "C/Toro, nº71",
                "streetName": "C/Toro",
                "buildingNumber": "nº 71",
                "stair": "1",
                "floor": 1,
                "doorNumber": "1A",
                "postalCode": "37002",
                "province": "Salamanca",
                "country": "ES",
            },
        },
    }
    response = client.request(**kwargs)
    assert_400(response)

    kwargs["json"] = {
        "name": "UXCALE POST",
        "line": "C/Toro, nº71",
        "streetName": "C/Toro",
        "buildingNumber": "nº 71",
        "stair": "1",
        "floor": 1,
        "doorNumber": "1A",
        "postalCode": "37002",
        "province": "Salamanca",
        "country": "ES",
    }
    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = f"/offices/{1}"
    response = client.request(**kwargs)
    assert_204(response)


@pytest.mark.order(15)
def test_delete_offices_office_id(client: MyHTTPXClient):
    """Test case for delete_offices_office_id

    Delete specific office.
    """
    kwargs = {
        "method": "DELETE",
        "url": f"/offices/{56}",
        "headers": REQUEST_HEADERS,
    }
    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = f"/offices/{1}"
    response = client.request(**kwargs)
    assert_204(response)
