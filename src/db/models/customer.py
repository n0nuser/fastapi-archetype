from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base import BaseTimestamps


class Customer(BaseTimestamps):
    name: Mapped[str] = mapped_column(String, nullable=False)
    addresses: Mapped[list["Address"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan", lazy="subquery"
    )


class Address(BaseTimestamps):
    customer_id: Mapped[UUID] = mapped_column(ForeignKey("customer_table.id"))
    customer: Mapped["Customer"] = relationship(back_populates="addresses")
    street: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str] = mapped_column(String, nullable=False)
    postal_code: Mapped[str] = mapped_column(String, nullable=False)
