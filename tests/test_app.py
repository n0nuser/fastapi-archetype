"""Smoke tests for the application entrypoint."""

from fastapi.testclient import TestClient

from src.app import app


def test_health_check_returns_ok_status() -> None:
    client = TestClient(app, base_url="http://localhost")
    response = client.get("/health-check")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ko"}


def test_prometheus_metrics_are_exposed() -> None:
    client = TestClient(app, base_url="http://localhost")
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_request_duration_seconds" in response.text


def test_openapi_spec_is_served() -> None:
    client = TestClient(app, base_url="http://localhost")
    response = client.get("/api/customer-system/openapi.json")

    assert response.status_code == 200
    # /metrics is scraped by Prometheus and intentionally kept out of the contract.
    assert sorted(response.json()["paths"]) == [
        "/api/customer-system/auth/forgot-password",
        "/api/customer-system/auth/jwt/login",
        "/api/customer-system/auth/jwt/logout",
        "/api/customer-system/auth/register",
        "/api/customer-system/auth/request-verify-token",
        "/api/customer-system/auth/reset-password",
        "/api/customer-system/auth/verify",
        "/api/customer-system/users/me",
        "/api/customer-system/users/{id}",
        "/api/customer-system/v1/customers",
        "/api/customer-system/v1/customers/{customerId}",
        "/api/customer-system/v1/customers/{customerId}/addresses",
        "/api/customer-system/v1/customers/{customerId}/addresses/{addressId}",
        "/health-check",
    ]
