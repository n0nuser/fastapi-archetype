from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base import Base

if TYPE_CHECKING:
    from src.db.models.user import User


class Token(Base):
    token: Mapped[str] = mapped_column(primary_key=True, index=True)
    authenticates_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id"),
    )
    authenticates: Mapped[User] = relationship(back_populates="refresh_tokens")
