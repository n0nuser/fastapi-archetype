"""Test data builders for customer and address entities."""

from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.repository.models.base import BaseTimestamps
from src.repository.models.customer import Address, Customer


class Widget(BaseTimestamps):
    """Minimal model with a nullable text column for exercising generic CRUD."""

    label: Mapped[str | None] = mapped_column(String, nullable=True)


def build_customer(name: str = "John Doe") -> Customer:
    return Customer(name=name)


def build_address(
    customer_id: UUID,
    street: str = "123 Main St",
    city: str = "Anytown",
    country: str = "USA",
    postal_code: str = "12345",
) -> Address:
    return Address(
        customer_id=customer_id,
        street=street,
        city=city,
        country=country,
        postal_code=postal_code,
    )
