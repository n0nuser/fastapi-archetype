"""Fixtures for CRUDBase unit tests against an in-memory SQLite database."""

from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import Float, ForeignKey, String, Uuid, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship
from sqlalchemy.pool import StaticPool

from fastapi_crud_base.base import CRUDBase


class Base(DeclarativeBase):
    """Standalone declarative base for the test models."""


class Gadget(Base):
    """Related model used to exercise relationship filters."""

    __tablename__ = "gadgets"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100))


class Widget(Base):
    """Primary test model."""

    __tablename__ = "widgets"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100))
    nickname: Mapped[str | None] = mapped_column(String(100), default=None)
    price: Mapped[float] = mapped_column(Float)
    gadget_id: Mapped[UUID | None] = mapped_column(ForeignKey("gadgets.id"), nullable=True)
    gadget: Mapped[Gadget | None] = relationship()


class Removable(Base):
    """Model supporting soft deletes."""

    __tablename__ = "removables"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100))
    deleted_on: Mapped[datetime | None] = mapped_column(default=None)

    def soft_delete(self) -> "Removable":
        """Mark the record as deleted by stamping ``deleted_on``."""
        self.deleted_on = datetime.now(UTC)
        return self


@pytest.fixture
def db_session() -> Session:
    """Provide a fresh in-memory SQLite session per test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def widget_crud() -> CRUDBase[Widget]:
    """CRUD bound to the Widget model."""
    return CRUDBase(Widget)


@pytest.fixture
def removable_crud() -> CRUDBase[Removable]:
    """CRUD bound to the soft-delete-capable model."""
    return CRUDBase(Removable)


@pytest.fixture
def make_widget() -> Callable[..., Widget]:
    """Factory for Widget rows."""

    def _make(
        name: str,
        price: float = 10.0,
        gadget: Gadget | None = None,
        nickname: str | None = None,
    ) -> Widget:
        return Widget(name=name, price=price, gadget=gadget, nickname=nickname)

    return _make


@pytest.fixture
def make_removable() -> Callable[..., Removable]:
    """Factory for soft-delete-capable rows."""

    def _make(name: str = "Soft") -> Removable:
        return Removable(name=name)

    return _make


@pytest.fixture
def gadgets(db_session: Session) -> list[Gadget]:
    """Two gadgets used by relationship-filter tests."""
    session_gadgets = [Gadget(name="Phone"), Gadget(name="Laptop")]
    db_session.add_all(session_gadgets)
    db_session.commit()
    return session_gadgets


@pytest.fixture
def widget_model() -> type[Widget]:
    """The Widget class itself, for schema-level operations."""
    return Widget
