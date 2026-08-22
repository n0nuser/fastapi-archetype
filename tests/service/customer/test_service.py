"""Integration tests for the customer application service against real Postgres."""

import pytest
from sqlalchemy.orm import Session

from src.controller.api.schemas.customer import AddressBase, CustomerCreate, CustomerUpdate
from src.repository.crud.address import address_crud
from src.repository.crud.customer import customer_crud
from src.repository.exceptions import ElementNotFoundError
from src.service.customer.service import CustomerApplicationService
from tests.factories import build_address, build_customer

pytestmark = pytest.mark.integration


def address_payload(street: str = "123 Main St", city: str = "Anytown") -> AddressBase:
    return AddressBase(street=street, city=city, country="USA", postalCode="12345")


def create_customer_with_address(
    db_session: Session,
    name: str,
    street: str,
    city: str = "Anytown",
) -> None:
    customer = customer_crud.create(db_session, build_customer(name=name))
    address_crud.create(
        db_session,
        build_address(customer_id=customer.id, street=street, city=city),
    )


def test_post_customer_creates_customer_and_addresses(db_session: Session) -> None:
    payload = CustomerCreate(
        name="John Doe",
        addresses=[address_payload(), address_payload("456 Elm St")],
    )

    customer_id = CustomerApplicationService.post_customer(db_session, payload)

    detail = CustomerApplicationService.get_customer_id(db_session, customer_id)
    assert detail.customerId == str(customer_id)
    assert detail.name == "John Doe"
    assert sorted(address.street for address in detail.addresses) == ["123 Main St", "456 Elm St"]


def test_post_customer_without_addresses(db_session: Session) -> None:
    customer_id = CustomerApplicationService.post_customer(db_session, CustomerCreate(name="Jane"))

    detail = CustomerApplicationService.get_customer_id(db_session, customer_id)
    assert detail.addresses == []


def no_filters() -> dict[str, str | None]:
    return {"street": None, "city": None, "country": None, "postal_code": None}


def test_get_customers_returns_paginated_list_with_total(db_session: Session) -> None:
    for name in ("Alice", "Bob", "Carol"):
        create_customer_with_address(db_session, name, f"{name} Street")

    page_one, total = CustomerApplicationService.get_customers(
        db_session,
        limit=2,
        offset=0,
        **no_filters(),
    )
    page_two, _ = CustomerApplicationService.get_customers(
        db_session,
        limit=2,
        offset=2,
        **no_filters(),
    )

    names = [row.name for row in page_one] + [row.name for row in page_two]
    assert total == 3
    assert sorted(names) == ["Alice", "Bob", "Carol"]


@pytest.mark.parametrize(
    ("filters", "expected_names"),
    [
        ({"street": "Main"}, ["Main St Owner"]),
        ({"city": "Springfield"}, ["Springfield Owner"]),
        ({"postal_code": "99999"}, ["Zip Owner"]),
        (
            {"street": "nomatch"},
            [],
        ),
    ],
)
def test_get_customers_applies_address_filters(
    db_session: Session,
    filters: dict[str, str],
    expected_names: list[str],
) -> None:
    create_customer_with_address(db_session, "Main St Owner", "1 Main Street")
    create_customer_with_address(
        db_session,
        "Springfield Owner",
        "9 Oak Avenue",
        city="Springfield",
    )
    zip_owner = customer_crud.create(db_session, build_customer(name="Zip Owner"))
    address_crud.create(
        db_session,
        build_address(customer_id=zip_owner.id, street="3 Pine Road", postal_code="99999"),
    )

    customers, total = CustomerApplicationService.get_customers(
        db_session,
        limit=10,
        offset=0,
        **{**no_filters(), **filters},
    )

    assert sorted(row.name for row in customers) == expected_names
    assert total == len(expected_names)


def test_get_customer_id_raises_for_unknown_customer(db_session: Session) -> None:
    unknown_id = build_customer().id

    with pytest.raises(ElementNotFoundError):
        CustomerApplicationService.get_customer_id(db_session, unknown_id)


def test_put_customers_updates_name(db_session: Session) -> None:
    created = customer_crud.create(db_session, build_customer(name="Old Name"))

    CustomerApplicationService.put_customers(
        db_session,
        created.id,
        CustomerUpdate(name="New Name"),
    )

    assert customer_crud.get_by_id(db_session, created.id).name == "New Name"


def test_delete_customer_removes_customer_and_addresses(db_session: Session) -> None:
    created = customer_crud.create(db_session, build_customer(name="Doomed"))
    address_crud.create(db_session, build_address(customer_id=created.id))

    CustomerApplicationService.delete_customer(db_session, created.id)

    with pytest.raises(ElementNotFoundError):
        customer_crud.get_by_id(db_session, created.id)
    assert address_crud.count(db_session) == 0


def test_post_address_adds_address_to_existing_customer(db_session: Session) -> None:
    created = customer_crud.create(db_session, build_customer(name="Alice"))

    CustomerApplicationService.post_address(db_session, created.id, address_payload())

    detail = CustomerApplicationService.get_customer_id(db_session, created.id)
    assert [address.street for address in detail.addresses] == ["123 Main St"]


def test_post_address_raises_for_unknown_customer(db_session: Session) -> None:
    unknown_id = build_customer().id

    with pytest.raises(ElementNotFoundError):
        CustomerApplicationService.post_address(db_session, unknown_id, address_payload())


def test_delete_address_raises_for_unknown_address(db_session: Session) -> None:
    created = customer_crud.create(db_session, build_customer(name="Alice"))

    with pytest.raises(ElementNotFoundError):
        CustomerApplicationService.delete_address(db_session, created.id, created.id)
