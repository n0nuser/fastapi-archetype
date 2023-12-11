from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base import Base

if TYPE_CHECKING:
    from src.db.models.token import Token  # noqa: F401


class User(Base):
    # METADATA
    full_name: Mapped[str] = mapped_column(index=True, nullable=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(nullable=True)
    # AUTHENTICATION AND PERSISTENCE
    totp_secret: Mapped[Optional[str]] = mapped_column(nullable=True)
    totp_counter: Mapped[Optional[int]] = mapped_column(nullable=True)
    email_validated: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    refresh_tokens: Mapped[list["Token"]] = relationship(
        foreign_keys="[Token.authenticates_id]",
        back_populates="authenticates",
        lazy="dynamic",
    )
