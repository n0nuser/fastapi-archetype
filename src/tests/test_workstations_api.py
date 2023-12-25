import pytest
from fastapi import Response

from src.api.schemas.pagination import Pagination
from src.api.schemas.workstation_data import WorkstationData
from src.api.schemas.workstation_data_data import WorkstationDataData
from src.api.schemas.workstation_response import WorkstationResponse
from src.api.schemas.workstation_response_data_inner import \
    WorkstationResponseDataInner
from src.tests.conftest import MyHTTPXClient
from src.tests.utils import (REQUEST_HEADERS, assert_201, assert_204,
                             assert_400, assert_404)


def assert_200_workstation(response: Response):
    assert response.status_code == 200
    workstation_response = WorkstationResponse.parse_obj(response.json())
    assert isinstance(workstation_response, WorkstationResponse)
    assert isinstance(workstation_response.data[0], WorkstationResponseDataInner)
    assert isinstance(workstation_response.pagination, Pagination)


def assert_200_workstation_id(response: Response):
    assert response.status_code == 200
    workstation_response = WorkstationData.parse_obj(response.json())
    assert isinstance(workstation_response, WorkstationData)
    assert isinstance(workstation_response.data, WorkstationDataData)


@pytest.mark.order(10)
def test_get_offices_office_id_sectors_sector_id_workstations(client: MyHTTPXClient):
    """Test case for get_offices_office_id_sectors_sector_id_workstations

    List of Workstations.
    """
    params = [("limit", 10), ("offset", 0)]
    kwargs = {
        "method": "GET",
        "url": f"/offices/{56}/sectors/{56}/workstations",
        "headers": REQUEST_HEADERS,
        "params": params,
    }

    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = f"/offices/{1}/sectors/{56}/workstations"
    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = f"/offices/{1}/sectors/{1}/workstations"
    response = client.request(**kwargs)
    assert_200_workstation(response)


@pytest.mark.order(12)
def test_get_offices_office_id_sectors_sector_id_workstations_workstation_id(client: MyHTTPXClient):
    """Test case for get_offices_office_id_sectors_sector_id_workstations_workstation_id

    Wokstation information.
    """
    kwargs = {
        "method": "GET",
        "url": f"/offices/{56}/sectors/{56}/workstations/{56}",
        "headers": REQUEST_HEADERS,
    }

    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = f"/offices/{1}/sectors/{56}/workstations/{56}"
    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = f"/offices/{1}/sectors/{1}/workstations/{56}"
    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = f"/offices/{1}/sectors/{1}/workstations/{1}"
    response = client.request(**kwargs)
    assert_200_workstation_id(response)


@pytest.mark.order(9)
def test_post_offices_office_id_sectors_sector_id_workstations(client: MyHTTPXClient):
    """Test case for post_offices_office_id_sectors_sector_id_workstations

    Create a new workstations.
    """
    json_body = {
        "name": "Site 11",
        "position": 80,
        "xCoordinate": 20,
        "yCoordinate": 100,
        "rotation": 180,
        "isLocked": True,
    }
    kwargs = {
        "method": "POST",
        "url": f"/offices/{56}/sectors/{56}/workstations",
        "headers": REQUEST_HEADERS,
        "json": json_body,
    }
    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = f"/offices/{1}/sectors/{56}/workstations"
    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = f"/offices/{1}/sectors/{1}/workstations"
    response = client.request(**kwargs)
    assert_201(response)

    kwargs["json"] = {
        "data": {
            "name": "Site 11",
            "position": 80,
            "xCoordinate": 20,
            "yCoordinate": 100,
            "rotation": 180,
            "isLocked": True,
        },
    }
    response = client.request(**kwargs)
    assert_400(response)


@pytest.mark.order(11)
def test_put_offices_office_id_sectors_sector_id_workstation_workstation_id(client: MyHTTPXClient):
    """Test case for put_offices_office_id_sectors_sector_id_workstation_workstation_id

    Update information from a workstations.
    """
    json_body = {
        "name": "Site 11",
        "position": 80,
        "xCoordinate": 20,
        "yCoordinate": 100,
        "rotation": 180,
        "isLocked": True,
    }
    kwargs = {
        "method": "PUT",
        "url": f"/offices/{56}/sectors/{56}/workstations/{56}",
        "headers": REQUEST_HEADERS,
        "json": json_body,
    }
    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = f"/offices/{1}/sectors/{56}/workstations/{56}"
    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = f"/offices/{1}/sectors/{1}/workstations/{56}"
    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = f"/offices/{1}/sectors/{1}/workstations/{1}"
    response = client.request(**kwargs)
    assert_204(response)

    kwargs["json"] = {
        "data": {
            "name": "Site 11",
            "position": 80,
            "xCoordinate": 20,
            "yCoordinate": 100,
            "rotation": 180,
            "isLocked": True,
        },
    }
    response = client.request(**kwargs)
    assert_400(response)


@pytest.mark.order(13)
def test_delete_offices_office_id_sectors_sector_id_workstation_workstation_id(
    client: MyHTTPXClient,
):
    """Test case for delete_offices_office_id_sectors_sector_id_workstation_workstation_id

    Delete specific workstation.
    """
    kwargs = {
        "method": "DELETE",
        "url": f"/offices/{56}/sectors/{56}/workstations/{56}",
        "headers": REQUEST_HEADERS,
    }

    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = f"/offices/{1}/sectors/{56}/workstations/{56}"
    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = f"/offices/{1}/sectors/{1}/workstations/{56}"
    response = client.request(**kwargs)
    assert_404(response)

    kwargs["url"] = f"/offices/{1}/sectors/{1}/workstations/{1}"
    response = client.request(**kwargs)
    assert_204(response)
