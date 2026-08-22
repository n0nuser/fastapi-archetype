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
    response = client.get("/api/{{ cookiecutter.base_api_path }}/openapi.json")

    assert response.status_code == 200
    # /metrics is scraped by Prometheus and intentionally kept out of the contract.
    assert sorted(response.json()["paths"]) == [
        "/api/{{ cookiecutter.base_api_path }}/auth/forgot-password",
        "/api/{{ cookiecutter.base_api_path }}/auth/jwt/login",
        "/api/{{ cookiecutter.base_api_path }}/auth/jwt/logout",
        "/api/{{ cookiecutter.base_api_path }}/auth/register",
        "/api/{{ cookiecutter.base_api_path }}/auth/request-verify-token",
        "/api/{{ cookiecutter.base_api_path }}/auth/reset-password",
        "/api/{{ cookiecutter.base_api_path }}/auth/verify",
        "/api/{{ cookiecutter.base_api_path }}/users/me",
        "/api/{{ cookiecutter.base_api_path }}/users/{id}",
        "/api/{{ cookiecutter.base_api_path }}/v1/customers",
        "/api/{{ cookiecutter.base_api_path }}/v1/customers/{customerId}",
        "/api/{{ cookiecutter.base_api_path }}/v1/customers/{customerId}/addresses",
        "/api/{{ cookiecutter.base_api_path }}/v1/customers/{customerId}/addresses/{addressId}",
        "/health-check",
    ]
