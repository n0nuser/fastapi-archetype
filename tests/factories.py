"""Test data builders for customer and address entities."""

from uuid import UUID

from src.repository.models.customer import Address, Customer


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
