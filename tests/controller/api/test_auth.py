"""Integration tests for registration, JWT login and role-based access control."""

import pytest
from sqlalchemy import update

from src.repository.models.user import User

pytestmark = pytest.mark.integration

REGISTER = "/api/customer-system/auth/register"
LOGIN = "/api/customer-system/auth/jwt/login"
ME = "/api/customer-system/users/me"
USER_BY_ID = "/api/customer-system/users/{user_id}"

PASSWORD = "wonderful-secure-password"  # noqa: S105


def register(client, email="alice@example.com"):
    return client.post(REGISTER, json={"email": email, "password": PASSWORD})


def login(client, email="alice@example.com"):
    response = client.post(LOGIN, data={"username": email, "password": PASSWORD})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


class TestRegistration:
    def test_register_returns_user(self, client) -> None:
        response = register(client)

        assert response.status_code == 201
        body = response.json()
        assert body["email"] == "alice@example.com"
        assert body["is_superuser"] is False
        assert "hashed_password" not in body
        assert "password" not in body

    def test_register_rejects_duplicated_email(self, client) -> None:
        assert register(client).status_code == 201

        response = register(client)

        assert response.status_code == 400

    def test_register_rejects_invalid_email(self, client) -> None:
        response = register(client, email="not-an-email")

        # The global exception handler maps validation errors to 400.
        assert response.status_code == 400


class TestLogin:
    def test_login_returns_bearer_token(self, client) -> None:
        register(client)
        response = client.post(LOGIN, data={"username": "alice@example.com", "password": PASSWORD})

        assert response.status_code == 200
        assert response.json()["token_type"] == "bearer"  # noqa: S105
        assert response.json()["access_token"]

    def test_login_rejects_wrong_password(self, client) -> None:
        register(client)

        response = client.post(
            LOGIN, data={"username": "alice@example.com", "password": "wrong-password"}
        )

        assert response.status_code == 400

    def test_login_rejects_unknown_user(self, client) -> None:
        response = client.post(LOGIN, data={"username": "ghost@example.com", "password": PASSWORD})

        assert response.status_code == 400


class TestProfile:
    def test_me_returns_authenticated_user(self, client) -> None:
        register(client)
        headers = login(client)

        response = client.get(ME, headers=headers)

        assert response.status_code == 200
        assert response.json()["email"] == "alice@example.com"

    def test_me_requires_authentication(self, client) -> None:
        response = client.get(ME)

        assert response.status_code == 401


class TestRoleBasedAccess:
    def test_regular_user_cannot_read_other_users(self, client) -> None:
        register(client, email="alice@example.com")
        register(client, email="bob@example.com")
        headers = login(client, email="alice@example.com")
        bob_id = client.get(ME, headers=login(client, email="bob@example.com")).json()["id"]

        response = client.get(USER_BY_ID.format(user_id=bob_id), headers=headers)

        assert response.status_code == 403

    def test_superuser_can_manage_users(self, client, db_session) -> None:
        register(client, email="alice@example.com")
        headers = login(client, email="alice@example.com")

        # Promote Alice directly in the database; tokens carry the id only.
        db_session.execute(update(User).values(is_superuser=True))
        db_session.commit()

        response = client.get(ME, headers=headers)
        alice_id = response.json()["id"]

        fetched = client.get(USER_BY_ID.format(user_id=alice_id), headers=headers)

        assert fetched.status_code == 200
