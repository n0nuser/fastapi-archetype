"""User manager: fastapi-users business logic hooks."""

import logging
from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin

from src.core.config import settings
from src.repository.crud.user import SyncSQLAlchemyUserDatabase, get_user_db
from src.repository.models.user import User

logger = logging.getLogger(__name__)


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    """Manages registration, authentication, verification and password resets."""

    reset_password_token_secret = settings.RESET_PASSWORD_TOKEN_SECRET
    verification_token_secret = settings.VERIFICATION_TOKEN_SECRET

    async def on_after_register(self, user: User, _request: Request | None = None) -> None:
        """Log successful registrations."""
        logger.info("User %s has registered.", user.id)

    async def on_after_forgot_password(
        self, user: User, token: str, _request: Request | None = None
    ) -> None:
        """Log reset requests.

        A production deployment should deliver ``token`` by email instead of
        logging it; this hook is the integration point for a mail sender.
        """
        logger.info("User %s has forgot their password. Reset token: %s", user.id, token)

    async def on_after_request_verify(
        self, user: User, token: str, _request: Request | None = None
    ) -> None:
        """Log verification requests; deliver ``token`` by email in production."""
        logger.info("Verification requested for user %s. Verification token: %s", user.id, token)


async def get_user_manager(
    user_db: Annotated[SyncSQLAlchemyUserDatabase, Depends(get_user_db)],
) -> AsyncGenerator[UserManager, None]:
    """FastAPI dependency yielding the application user manager."""
    yield UserManager(user_db)
