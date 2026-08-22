"""Unit tests for CRUDBase against an in-memory SQLite database."""

from uuid import UUID

import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from fastapi_crud_base import ElementNotFoundError, Filter


class TestCreate:
    def test_create_persists_and_populates_id(
        self, widget_crud, db_session: Session, make_widget
    ) -> None:
        created = widget_crud.create(db_session, make_widget("Alice"))

        assert created.id is not None
        assert widget_crud.get_by_id(db_session, created.id) == created

    def test_bulk_create_persists_all(self, widget_crud, db_session: Session, make_widget) -> None:
        rows = widget_crud.bulk_create(
            db_session,
            [make_widget("A"), make_widget("B"), make_widget("C")],
        )

        assert len(rows) == 3
        assert all(row.id is not None for row in rows)
        assert widget_crud.count(db_session) == 3


class TestRead:
    def test_get_by_id_missing_raises(self, widget_crud, db_session: Session) -> None:
        with pytest.raises(ElementNotFoundError, match="Widget"):
            widget_crud.get_by_id(db_session, row_id=UUID("00000000-0000-0000-0000-000000000000"))

    def test_get_one_by_field_exact_match(
        self, widget_crud, db_session: Session, make_widget
    ) -> None:
        created = widget_crud.create(db_session, make_widget("Bob"))

        assert widget_crud.get_one_by_field(db_session, field="name", value="Bob") == created

    def test_get_one_by_field_case_insensitive(
        self, widget_crud, db_session: Session, make_widget
    ) -> None:
        created = widget_crud.create(db_session, make_widget("Alice"))

        found = widget_crud.get_one_by_field(
            db_session, field="name", value="ALICE", case_insensitive=True
        )

        assert found == created

    def test_get_list_with_and_filters(self, widget_crud, db_session: Session, make_widget) -> None:
        widget_crud.bulk_create(
            db_session,
            [make_widget("Red", 5.0), make_widget("Blue", 15.0), make_widget("Red", 20.0)],
        )

        result = widget_crud.get_list(
            db_session,
            filters=[
                Filter(field="name", operator="eq", value="Red"),
                Filter(field="price", operator="gte", value=10.0),
            ],
        )

        assert len(result) == 1
        assert result[0].name == "Red"
        assert result[0].price == 20.0

    def test_get_list_with_or_filters(self, widget_crud, db_session: Session, make_widget) -> None:
        widget_crud.bulk_create(
            db_session,
            [make_widget("Red", 5.0), make_widget("Blue", 15.0), make_widget("Green", 25.0)],
        )

        result = widget_crud.get_list(
            db_session,
            filters=[
                Filter(field="name", operator="eq", value="Red"),
                Filter(field="name", operator="eq", value="Green"),
            ],
            filter_is_logic_and=False,
            order_by="name",
        )

        assert [row.name for row in result] == ["Green", "Red"]

    def test_get_list_orders_paginates(self, widget_crud, db_session: Session, make_widget) -> None:
        widget_crud.bulk_create(db_session, [make_widget(f"W{i}", float(i)) for i in range(5)])

        page = widget_crud.get_list(db_session, offset=1, limit=2, order_by="name")
        desc = widget_crud.get_list(db_session, order_by="name", order_direction="desc", limit=2)

        assert [row.name for row in page] == ["W1", "W2"]
        assert [row.name for row in desc] == ["W4", "W3"]

    def test_get_list_relationship_filter(
        self, widget_crud, db_session: Session, make_widget, gadgets
    ) -> None:
        widget_crud.bulk_create(
            db_session,
            [
                make_widget("WithPhone", gadget=gadgets[0]),
                make_widget("Alone"),
            ],
        )

        result = widget_crud.get_list(
            db_session,
            filters=[Filter(field="gadget.name", operator="eq", value="Phone")],
        )

        assert len(result) == 1
        assert result[0].name == "WithPhone"

    def test_count_join_aware(self, widget_crud, db_session: Session, make_widget, gadgets) -> None:
        # Two widgets share one gadget; a naive join would double-count them.
        widget_crud.bulk_create(
            db_session,
            [
                make_widget("One", gadget=gadgets[0]),
                make_widget("Two", gadget=gadgets[0]),
                make_widget("Three"),
            ],
        )

        assert widget_crud.count(db_session) == 3
        phone = Filter(field="gadget.name", operator="eq", value="Phone")
        assert widget_crud.count(db_session, filters=[phone]) == 2


class TestUpdateDelete:
    def test_update_merges_changes(self, widget_crud, db_session: Session, make_widget) -> None:
        created = widget_crud.create(db_session, make_widget("Old"))
        created.price = 99.0

        updated = widget_crud.update(db_session, created)

        assert updated.price == 99.0

    def test_bulk_update_applies_to_all(
        self, widget_crud, db_session: Session, make_widget
    ) -> None:
        rows = widget_crud.bulk_create(db_session, [make_widget("A"), make_widget("B")])
        for row in rows:
            row.price = 42.0

        updated = widget_crud.bulk_update(db_session, rows)

        assert all(row.price == 42.0 for row in updated)
        cheap = Filter(field="price", operator="eq", value=42.0)
        assert widget_crud.count(db_session, filters=[cheap]) == 2

    def test_delete_row_removes_record(self, widget_crud, db_session: Session, make_widget) -> None:
        created = widget_crud.create(db_session, make_widget("Doomed"))

        deleted = widget_crud.delete_row(db_session, created)

        assert deleted is created
        assert widget_crud.count(db_session) == 0

    def test_soft_delete_stamps_deleted_on(
        self, removable_crud, db_session: Session, make_removable
    ) -> None:
        created = removable_crud.create(db_session, make_removable())

        soft_deleted = removable_crud.soft_delete_row(db_session, created)

        assert soft_deleted.deleted_on is not None

    def test_soft_delete_unsupported_model_raises(
        self, widget_crud, db_session: Session, make_widget
    ) -> None:
        created = widget_crud.create(db_session, make_widget("Hard"))

        with pytest.raises(ValueError, match="soft delete"):
            widget_crud.soft_delete_row(db_session, created)


class TestUniqueValues:
    def test_excludes_nulls_and_empty_strings(
        self, widget_crud, db_session: Session, make_widget
    ) -> None:
        widget_crud.bulk_create(
            db_session,
            [
                make_widget("Red", nickname="x"),
                make_widget("Blue", nickname=""),
                make_widget("Green", nickname=None),
            ],
        )

        assert widget_crud.get_unique_values(db_session, column_name="nickname") == ["x"]
        values = widget_crud.get_unique_values(db_session, "nickname", include_nulls=True)
        assert sorted(values, key=str) == ["", None, "x"]

    def test_unknown_column_raises_attribute_error(self, widget_crud, db_session: Session) -> None:
        with pytest.raises(AttributeError, match="nonexistent"):
            widget_crud.get_unique_values(db_session, column_name="nonexistent")


class TestFilterModel:
    def test_rejects_unknown_operator(self) -> None:
        with pytest.raises(ValidationError):
            Filter(field="name", operator="regex", value="x")
