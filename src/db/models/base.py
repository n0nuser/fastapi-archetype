"""SQL Alchemy models declaration.
https://docs.sqlalchemy.org/en/20/orm/declarative_styles.html#example-two-dataclasses-with-declarative-table
Dataclass style for powerful autocompletion support.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (DeclarativeBase, Mapped, declared_attr,
                            mapped_column)
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid4,
    )

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class BaseTimestamps(Base):
    __abstract__ = True
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )


class BaseDeletedOn(Base):
    __abstract__ = True
    deleted_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
    )

    def soft_delete(self):
        self.deleted_on = datetime.now()
        return self
