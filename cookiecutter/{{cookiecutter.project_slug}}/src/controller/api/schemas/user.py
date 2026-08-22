"""Pydantic schemas for user management."""

from uuid import UUID

from fastapi_users import schemas


class UserRead(schemas.BaseUser[UUID]):
    """User representation returned by the API."""


class UserCreate(schemas.BaseUserCreate):
    """Payload accepted at registration."""


class UserUpdate(schemas.BaseUserUpdate):
    """Payload accepted for profile updates."""
