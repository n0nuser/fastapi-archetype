"""Smoke tests for the application entrypoint."""

from fastapi.testclient import TestClient

from src.app import app


def test_health_check_returns_ok_status() -> None:
    client = TestClient(app, base_url="http://localhost")
    response = client.get("/health-check")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ko"}


def test_openapi_spec_is_served() -> None:
    client = TestClient(app, base_url="http://localhost")
    response = client.get("/api/customer-system/openapi.json")

    assert response.status_code == 200
    assert sorted(response.json()["paths"]) == [
        "/api/customer-system/v1/customers",
        "/api/customer-system/v1/customers/{customerId}",
        "/api/customer-system/v1/customers/{customerId}/addresses",
        "/api/customer-system/v1/customers/{customerId}/addresses/{addressId}",
        "/health-check",
    ]
