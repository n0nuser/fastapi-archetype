# fastapi-crud-base

Reusable CRUD base for [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/) models:
a generic, typed `CRUDBase` with filtering, pagination, ordering, bulk operations
and soft deletes. Framework-agnostic — it only depends on SQLAlchemy and Pydantic,
and works with any Python web framework (FastAPI, Flask, Django, CLI scripts…).

## Features

- **Typed CRUD**: `CRUDBase[Model]` is generically typed over your SQLAlchemy models.
- **Filtering**: declarative `Filter(field, operator, value)` objects supporting
  `eq`, `neq`, `contains`, `not_contains`, `gt`, `gte`, `lt`, `lte`, including
  filters across relationships (`"addresses.street"`) and case-insensitive matching.
- **Pagination & ordering**: `offset`/`limit` plus `order_by`/`order_direction`.
- **Bulk operations**: `bulk_create` and `bulk_update` in single transactions.
- **Soft deletes**: `soft_delete_row` for models exposing a `deleted_on` attribute.
- **Aggregates**: `count` (join-aware) and `get_unique_values`.

## Installation

```bash
pip install fastapi-crud-base
# or
uv add fastapi-crud-base
```

Requires Python 3.12+ and SQLAlchemy 2.0+.

## Quickstart

```python
from uuid import UUID, uuid4

from fastapi_crud_base import CRUDBase, ElementNotFoundError, Filter
from sqlalchemy import String, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100))


customer_crud = CRUDBase(Customer)

created = customer_crud.create(session, Customer(name="Alice"))
found = customer_crud.get_by_id(session, created.id)
adults = customer_crud.get_list(
    session,
    filters=[Filter(field="name", operator="contains", value="li")],
    order_by="name",
)
try:
    customer_crud.get_by_id(session, uuid4())
except ElementNotFoundError as error:
    print(error)  # Customer with ID: ... not found.
```

## Development

```bash
uv sync --all-groups
uv run pytest
```

## License

MIT — see [LICENSE](LICENSE).
