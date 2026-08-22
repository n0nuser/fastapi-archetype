"""Integration tests for the customer HTTP API against real Postgres."""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.core.config import settings

pytestmark = pytest.mark.integration

CUSTOMERS_URL = f"/api/{settings.BASE_API_PATH}/v1/customers"

CUSTOMER_PAYLOAD = {
    "name": "John Doe",
    "addresses": [
        {"street": "123 Main St", "city": "Anytown", "country": "USA", "postalCode": "12345"},
    ],
}


def create_customer(client: TestClient, payload: dict | None = None) -> str:
    """Create a customer through the API and return its id parsed from Location."""
    response = client.post(CUSTOMERS_URL, json=payload or CUSTOMER_PAYLOAD)
    assert response.status_code == 201, response.text
    return response.headers["location"].rstrip("/").rsplit("/", maxsplit=1)[-1]


def test_post_customer_returns_201_and_location_header(client: TestClient) -> None:
    response = client.post(CUSTOMERS_URL, json=CUSTOMER_PAYLOAD)

    assert response.status_code == 201
    assert "location" in response.headers


def test_get_customer_detail_returns_full_payload(client: TestClient) -> None:
    customer_id = create_customer(client)

    response = client.get(f"{CUSTOMERS_URL}/{customer_id}")

    assert response.status_code == 200
    assert response.json() == {
        "customerId": customer_id,
        "name": "John Doe",
        "addresses": [
            {
                "addressId": response.json()["addresses"][0]["addressId"],
                "street": "123 Main St",
                "city": "Anytown",
                "country": "USA",
                "postalCode": "12345",
            },
        ],
    }


def test_get_customers_list_returns_data_and_pagination(client: TestClient) -> None:
    first = create_customer(client)
    second = create_customer(client, {**CUSTOMER_PAYLOAD, "name": "Jane Roe"})

    response = client.get(CUSTOMERS_URL)

    assert response.status_code == 200
    body = response.json()
    # Default ordering is by UUID id, so compare without relying on row order.
    assert sorted(body["data"], key=lambda row: row["name"]) == [
        {"customerId": first, "name": "John Doe"},
        {"customerId": second, "name": "Jane Roe"},
    ]
    assert body["pagination"] is not None


def test_put_customer_updates_name(client: TestClient) -> None:
    customer_id = create_customer(client)

    updated = client.put(f"{CUSTOMERS_URL}/{customer_id}", json={"name": "Renamed"})
    detail = client.get(f"{CUSTOMERS_URL}/{customer_id}")

    assert updated.status_code == 204
    assert detail.json()["name"] == "Renamed"


def test_delete_customer_removes_it(client: TestClient) -> None:
    customer_id = create_customer(client)

    deleted = client.delete(f"{CUSTOMERS_URL}/{customer_id}")
    fetched = client.get(f"{CUSTOMERS_URL}/{customer_id}")

    assert deleted.status_code == 204
    assert fetched.status_code == 404


def test_get_unknown_customer_returns_404_error_payload(client: TestClient) -> None:
    response = client.get(f"{CUSTOMERS_URL}/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["messages"]


def test_post_customer_with_invalid_body_returns_400(client: TestClient) -> None:
    # The exception manager maps request validation errors to 400 by design.
    response = client.post(CUSTOMERS_URL, json={"addresses": []})

    assert response.status_code == 400
    assert response.json()["messages"]


def test_address_lifecycle_through_api(client: TestClient) -> None:
    customer_id = create_customer(client)
    address_url = f"{CUSTOMERS_URL}/{customer_id}/addresses"
    payload = {
        "street": "9 Oak Ave",
        "city": "Springfield",
        "country": "USA",
        "postalCode": "99999",
    }

    created = client.post(address_url, json=payload)
    address_id = created.headers["location"].rstrip("/").rsplit("/", maxsplit=1)[-1]
    updated = client.put(f"{address_url}/{address_id}", json={**payload, "street": "12 Cedar Lane"})
    detail = client.get(f"{CUSTOMERS_URL}/{customer_id}")

    assert created.status_code == 201
    assert updated.status_code == 204
    updated_address = next(
        address for address in detail.json()["addresses"] if address["addressId"] == address_id
    )
    assert updated_address["street"] == "12 Cedar Lane"
