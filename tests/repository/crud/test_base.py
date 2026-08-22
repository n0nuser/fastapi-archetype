"""Integration tests for CRUDBase against a real Postgres database."""

from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.repository.crud.address import address_crud
from src.repository.crud.base import Filter
from src.repository.crud.customer import customer_crud
from src.repository.exceptions import ElementNotFoundError
from src.repository.models.customer import Customer
from tests.factories import build_address, build_customer

pytestmark = pytest.mark.integration


@pytest.fixture
def alice(db_session: Session) -> Customer:
    return customer_crud.create(db_session, build_customer(name="Alice"))


@pytest.fixture
def bob(db_session: Session) -> Customer:
    return customer_crud.create(db_session, build_customer(name="Bob"))


def test_create_persists_row(db_session: Session) -> None:
    created = customer_crud.create(db_session, build_customer(name="Alice"))

    fetched = customer_crud.get_by_id(db_session, created.id)
    assert fetched.name == "Alice"


def test_get_by_id_raises_when_missing(db_session: Session) -> None:
    with pytest.raises(ElementNotFoundError, match="not found"):
        customer_crud.get_by_id(db_session, uuid4())


def test_get_one_by_field_returns_match(db_session: Session, alice: Customer) -> None:
    found = customer_crud.get_one_by_field(db_session, "name", "Alice")

    assert found.id == alice.id


@pytest.mark.usefixtures("alice")
def test_get_one_by_field_raises_when_missing(db_session: Session) -> None:
    with pytest.raises(ElementNotFoundError):
        customer_crud.get_one_by_field(db_session, "name", "Charlie")


@pytest.mark.usefixtures("alice")
def test_get_one_by_fields_returns_match_on_all_filters(
    db_session: Session,
    bob: Customer,
) -> None:
    address = address_crud.create(db_session, build_address(customer_id=bob.id))

    found = address_crud.get_one_by_fields(
        db_session,
        filters=[
            Filter(field="customer_id", operator="eq", value=str(bob.id)),
            Filter(field="id", operator="eq", value=str(address.id)),
        ],
    )

    assert found.id == address.id


@pytest.mark.usefixtures("alice", "bob")
@pytest.mark.parametrize(
    ("operator", "value", "expected_names"),
    [
        ("eq", "Alice", ["Alice"]),
        ("neq", "Alice", ["Bob"]),
        ("contains", "lic", ["Alice"]),
        ("not_contains", "lic", ["Bob"]),
        ("gt", "Alice", ["Bob"]),
        ("gte", "Alice", ["Alice", "Bob"]),
        ("lt", "Bob", ["Alice"]),
        ("lte", "Bob", ["Alice", "Bob"]),
    ],
)
def test_get_list_filter_operators(
    db_session: Session,
    operator: str,
    value: str,
    expected_names: list[str],
) -> None:
    result = customer_crud.get_list(
        db_session,
        filters=[Filter(field="name", operator=operator, value=value)],
    )

    assert sorted(row.name for row in result) == expected_names


def test_get_filter_expression_rejects_unknown_operator() -> None:
    with pytest.raises(ValueError, match="not supported"):
        customer_crud._get_filter_expression(Customer.name, "startswith", "A")  # noqa: SLF001


def test_filter_model_validates_operator_at_construction() -> None:
    with pytest.raises(ValidationError):
        Filter(field="name", operator="startswith", value="A")


@pytest.mark.usefixtures("alice", "bob")
def test_get_list_or_logic_matches_any_filter(db_session: Session) -> None:
    result = customer_crud.get_list(
        db_session,
        filters=[
            Filter(field="name", operator="eq", value="Alice"),
            Filter(field="name", operator="eq", value="Bob"),
        ],
        filter_is_logic_and=False,
    )

    assert sorted(row.name for row in result) == ["Alice", "Bob"]


@pytest.mark.usefixtures("alice", "bob")
def test_get_list_and_logic_matches_nothing_when_conflicting(db_session: Session) -> None:
    result = customer_crud.get_list(
        db_session,
        filters=[
            Filter(field="name", operator="eq", value="Alice"),
            Filter(field="name", operator="eq", value="Bob"),
        ],
        filter_is_logic_and=True,
    )

    assert result == []


@pytest.mark.usefixtures("alice", "bob")
def test_get_list_orders_and_paginates(db_session: Session) -> None:
    ascending = customer_crud.get_list(db_session, order_by="name", order_direction="asc")
    descending = customer_crud.get_list(db_session, order_by="name", order_direction="desc")
    page = customer_crud.get_list(db_session, offset=1, limit=1, order_by="name")

    assert [row.name for row in ascending] == ["Alice", "Bob"]
    assert [row.name for row in descending] == ["Bob", "Alice"]
    assert [row.name for row in page] == ["Bob"]


@pytest.mark.usefixtures("alice")
def test_get_list_join_fields_inner_joins_addresses(
    db_session: Session,
    bob: Customer,
) -> None:
    address_crud.create(db_session, build_address(customer_id=bob.id))

    joined = customer_crud.get_list(db_session, join_fields=["addresses"])

    # Alice has no addresses and is excluded by the inner join.
    assert [row.name for row in joined] == ["Bob"]


@pytest.mark.usefixtures("alice", "bob")
def test_count_counts_rows_and_respects_filters(db_session: Session) -> None:
    total = customer_crud.count(db_session)
    filtered = customer_crud.count(
        db_session,
        filters=[Filter(field="name", operator="eq", value="Alice")],
    )

    assert total == 2
    assert filtered == 1


@pytest.mark.usefixtures("bob")
def test_count_with_relationship_filters_does_not_inflate_total(db_session: Session) -> None:
    alice = customer_crud.create(db_session, build_customer(name="Solo"))
    address_crud.create(db_session, build_address(customer_id=alice.id))

    total = customer_crud.count(
        db_session,
        filters=[Filter(field="addresses.street", operator="contains", value="Main")],
    )

    assert total == 1


def test_update_merges_changes(db_session: Session, alice: Customer) -> None:
    alice.name = "Alicia"

    updated = customer_crud.update(db_session, alice)

    fetched = customer_crud.get_by_id(db_session, alice.id)
    assert updated.name == "Alicia"
    assert fetched.name == "Alicia"


def test_delete_row_removes_record(db_session: Session, alice: Customer) -> None:
    customer_crud.delete_row(db_session, alice)

    with pytest.raises(ElementNotFoundError):
        customer_crud.get_by_id(db_session, alice.id)


@pytest.mark.usefixtures("alice")
def test_soft_delete_row_rejects_model_without_deleted_on(db_session: Session) -> None:
    target = customer_crud.get_one_by_field(db_session, "name", "Alice")

    with pytest.raises(ValueError, match="soft delete"):
        customer_crud.soft_delete_row(db_session, target)
