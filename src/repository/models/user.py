"""Application user model managed by fastapi-users."""

from fastapi_users.db import SQLAlchemyBaseUserTableUUID

from src.repository.models.base import BaseTimestamps


class User(SQLAlchemyBaseUserTableUUID, BaseTimestamps):
    """Application user with authentication fields from fastapi-users.

    The table is named ``users`` because ``user`` is a reserved word in
    PostgreSQL; the shared ``Base`` metadata keeps it visible to Alembic.
    """

    __tablename__ = "users"
