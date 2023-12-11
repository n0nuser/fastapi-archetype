# coding: utf-8

import pytest
from requests import Response

from src.api.schemas.pagination import Pagination
from src.api.schemas.sector_data import SectorData
from src.api.schemas.sector_data_data import SectorDataData
from src.api.schemas.sector_response import SectorResponse
from src.api.schemas.sector_response_data_inner import SectorResponseDataInner
from src.tests.conftest import MyHTTPXClient
from src.tests.utils import REQUEST_HEADERS, assert_201, assert_204, assert_400, assert_404


def assert_200_sector(response: Response):
    assert response.status_code == 200
    sector_response = SectorResponse.parse_obj(response.json())
    assert isinstance(sector_response, SectorResponse)
    assert isinstance(sector_response.data[0], SectorResponseDataInner)
    assert isinstance(sector_response.pagination, Pagination)


def assert_200_sector_id(response: Response):
    assert response.status_code == 200
    sector_response = SectorData.parse_obj(response.json())
    assert isinstance(sector_response, SectorData)
    assert isinstance(sector_response.data, SectorDataData)


@pytest.mark.order(6)
def test_get_offices_office_id_sectors(client: MyHTTPXClient):
    """Test case for get_offices_office_id_sectors

    List of sectors.
    """
    params = [("limit", 10), ("offset", 0)]
    kwargs = {
        "method": "GET",
        "url": "/offices/{officeId}/sectors".format(officeId=56),
        "headers": REQUEST_HEADERS,
        "params": params,
    }

    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = "/offices/{officeId}/sectors".format(officeId=1)
    response = client.request(**kwargs)
    assert_200_sector(response)


@pytest.mark.order(8)
def test_get_offices_office_id_sectors_sector_id(client: MyHTTPXClient):
    """Test case for get_offices_office_id_sectors_sector_id

    Sector information.
    """

    kwargs = {
        "method": "GET",
        "url": "/offices/{officeId}/sectors/{sectorId}".format(officeId=56, sectorId=56),
        "headers": REQUEST_HEADERS,
    }
    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = "/offices/{officeId}/sectors/{sectorId}".format(officeId=1, sectorId=56)
    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = "/offices/{officeId}/sectors/{sectorId}".format(officeId=1, sectorId=1)
    response = client.request(**kwargs)
    assert_200_sector_id(response)


@pytest.mark.order(5)
def test_post_offices_office_id_sectors(client: MyHTTPXClient):
    """Test case for post_offices_office_id_sectors

    Create a new sector.
    """
    post_offices_office_id_sectors_request = {"name": "O+D", "isPhysical": False}
    kwargs = {
        "method": "POST",
        "url": "/offices/{officeId}/sectors".format(officeId=56),
        "headers": REQUEST_HEADERS,
        "json": post_offices_office_id_sectors_request,
    }

    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = "/offices/{officeId}/sectors".format(officeId=1)
    response = client.request(**kwargs)
    assert_201(response)

    kwargs["json"] = {"data": {"name": "O+D", "isPhysical": False}}
    response = client.request(**kwargs)


@pytest.mark.order(7)
def test_put_offices_office_id_sectors_sector_id(client: MyHTTPXClient):
    """Test case for put_offices_office_id_sectors_sector_id

    Update information from a sector.
    """
    post_offices_office_id_sectors_request = {"name": "O+D", "isPhysical": False}
    kwargs = {
        "method": "PUT",
        "url": "/offices/{officeId}/sectors/{sectorId}".format(officeId=56, sectorId=56),
        "headers": REQUEST_HEADERS,
        "json": post_offices_office_id_sectors_request,
    }

    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = "/offices/{officeId}/sectors/{sectorId}".format(officeId=1, sectorId=56)
    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = "/offices/{officeId}/sectors/{sectorId}".format(officeId=1, sectorId=1)
    response = client.request(**kwargs)
    assert_204(response)

    kwargs["json"] = {"data": {"name": "O+D", "isPhysical": False}}
    response = client.request(**kwargs)
    assert_400(response)


@pytest.mark.order(14)
def test_delete_offices_office_id_sectors_sector_id(client: MyHTTPXClient):
    """Test case for delete_offices_office_id_sectors_sector_id

    Delete specific sector.
    """
    kwargs = {
        "method": "DELETE",
        "url": "/offices/{officeId}/sectors/{sectorId}".format(officeId=56, sectorId=56),
        "headers": REQUEST_HEADERS,
    }

    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = "/offices/{officeId}/sectors/{sectorId}".format(officeId=1, sectorId=56)
    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = "/offices/{officeId}/sectors/{sectorId}".format(officeId=1, sectorId=1)
    response = client.request(**kwargs)
    assert_204(response)
