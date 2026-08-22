"""Synchronous database adapter exposing the User model to fastapi-users.

``fastapi-users-db-sqlalchemy`` only ships an ``AsyncSession`` adapter, while
this archetype runs a synchronous SQLAlchemy stack (psycopg2). This adapter
implements the same interface against a plain ``Session``; queries run inline
within the event loop thread, matching the existing CRUD layer's behaviour.
"""

from collections.abc import AsyncGenerator
from typing import Annotated, Any

from fastapi import Depends
from fastapi_users.db import BaseUserDatabase
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.repository.models.user import User
from src.repository.session import get_db_session


class SyncSQLAlchemyUserDatabase(BaseUserDatabase[User, Any]):
    """fastapi-users adapter backed by a synchronous SQLAlchemy session."""

    def __init__(self, session: Session, user_table: type[User]) -> None:
        """Bind the adapter to a request-scoped session."""
        self.session = session
        self.user_table = user_table

    async def get(self, user_id: Any) -> User | None:  # noqa: ANN401
        """Fetch a user by primary key."""
        return self.session.get(self.user_table, user_id)

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by email, case-insensitively."""
        statement = select(self.user_table).where(
            func.lower(self.user_table.email) == email.lower()
        )
        return self.session.scalars(statement).first()

    async def create(self, create_dict: dict[str, Any]) -> User:
        """Persist a new user from validated attribute values."""
        user = self.user_table(**create_dict)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    async def update(self, user: User, update_dict: dict[str, Any]) -> User:
        """Apply a partial update to an existing user."""
        for field, value in update_dict.items():
            setattr(user, field, value)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        """Remove a user permanently."""
        self.session.delete(user)
        self.session.commit()

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> User | None:
        """OAuth accounts are not configured in this archetype."""
        msg = "OAuth accounts are not configured."
        raise NotImplementedError(msg)

    async def add_oauth_account(self, user: User, create_dict: dict[str, Any]) -> User:
        """OAuth accounts are not configured in this archetype."""
        msg = "OAuth accounts are not configured."
        raise NotImplementedError(msg)

    async def update_oauth_account(self, user: User, update_dict: dict[str, Any]) -> User:
        """OAuth accounts are not configured in this archetype."""
        msg = "OAuth accounts are not configured."
        raise NotImplementedError(msg)


async def get_user_db(
    session: Annotated[Session, Depends(get_db_session)],
) -> AsyncGenerator[SyncSQLAlchemyUserDatabase, None]:
    """Yield the fastapi-users database adapter bound to the request session."""
    yield SyncSQLAlchemyUserDatabase(session, User)
