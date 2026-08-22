"""CRUD object with default methods to Create, Read, Update, Delete (CRUD)."""

import logging
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Literal
from uuid import UUID

from pydantic import UUID4, BaseModel, Field
from sqlalchemy import String, func, or_, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Query as SQLQuery
from sqlalchemy.orm import Session

from src.repository.exceptions import ElementNotFoundError
from src.repository.models.base import Base

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from collections.abc import Callable


class Filter(BaseModel):
    """Filter to be applied to a query."""

    field: str = Field(..., examples=["name"])
    operator: Literal["eq", "neq", "contains", "not_contains", "gt", "gte", "lt", "lte"] = Field(
        ...,
        examples=["eq"],
    )
    value: str | int | float | bool | UUID = Field(..., examples=["John Doe"])


class CRUDBase[ModelType: Base]:
    """CRUD object with default methods to Create, Read, Update, Delete (CRUD)."""

    def __init__(self: "CRUDBase[ModelType]", model: type[ModelType]) -> None:
        """CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def _get_filter_expression(
        self,
        filter_field: Any,  # noqa: ANN401
        operator: str,
        value: any,
        case_insensitive: bool = False,  # noqa: FBT001, FBT002
    ) -> SQLQuery:
        """
        Return the filter expression based on the operator and value.

        Args:
            filter_field: The SQLAlchemy model field to apply the filter on.
            operator: The filter operation to perform (e.g., "eq", "neq").
            value: The value to compare the field against.
            case_insensitive: If True, string comparisons ignore letter case.
                PostgreSQL compares strings case-sensitively by default, so
                this flag is what enables insensitive matching there; on
                MySQL with *_ci collations both modes behave the same.

        Returns:
            An SQLAlchemy query object representing the filter expression.

        Raises:
            ValueError: If the operator is not supported.
        """
        operators: dict[str, Callable[[any], SQLQuery]] = {
            "eq": lambda f: f == value,
            "neq": lambda f: f != value,
            "contains": lambda f: f.contains(value),
            "not_contains": lambda f: ~f.contains(value),
            "gt": lambda f: f > value,
            "gte": lambda f: f >= value,
            "lt": lambda f: f < value,
            "lte": lambda f: f <= value,
        }

        if operator not in operators:
            msg = f"Operator {operator} not supported."
            raise ValueError(msg)
        if case_insensitive and isinstance(value, str):
            filter_field = func.lower(filter_field)
            value = value.lower()
        return operators[operator](filter_field)

    def _resolve_field(self, field_path: str) -> tuple[str | None, Any]:
        """Resolve a dotted field path to its relationship name and final attribute.

        Args:
            field_path: Dotted path to a column, e.g. "name" or "addresses.street".

        Returns:
            Tuple with the relationship name (only when the path crosses one,
            e.g. "addresses") and the resolved column attribute.
        """
        field_parts = field_path.split(".")
        relationship_name = field_parts[0] if len(field_parts) > 1 else None
        filter_field = getattr(self.model, field_parts[0])
        for part in field_parts[1:]:
            filter_field = getattr(filter_field.property.mapper.class_, part)
        return relationship_name, filter_field

    def _get_filters(
        self,
        items: list["Filter"],
        case_insensitive: bool = False,  # noqa: FBT001, FBT002
    ) -> list[SQLQuery]:
        """
        Get the filters to be applied to a query.

        Args:
            items: A list of Filter objects specifying the filters to apply.
            case_insensitive: If True, string comparisons ignore letter case.

        Returns:
            A list of SQLAlchemy query objects representing the filters to be applied.
        """
        filter_clauses = []
        for filter_obj in items:
            _, filter_field = self._resolve_field(filter_obj.field)
            filter_clauses.append(
                self._get_filter_expression(
                    filter_field,
                    filter_obj.operator,
                    filter_obj.value,
                    case_insensitive,
                )
            )
        return filter_clauses

    def get_by_id(
        self: "CRUDBase[ModelType]",
        db: Session,
        row_id: int | UUID4,
    ) -> ModelType:
        """Returns an object of the model specified.

        Args:
            db (Session): Database session.
            row_id (int): ID of the row in the DB.

        Returns:
            ModelType: Element.

        Raises:
            ElementNotFoundError: If the element is not found.
        """
        logger.info("Entering...")
        logger.debug("Getting %s with ID: %s", self.model.__name__, row_id)
        if data := db.query(self.model).filter(self.model.id == row_id).first():
            logger.debug("Found %s with ID: %s", self.model.__name__, row_id)
            logger.info("Exiting...")
            return data
        error_msg = f"{self.model.__name__} with ID: {row_id} not found."
        logger.error(error_msg)
        logger.info("Exiting...")
        raise ElementNotFoundError(error_msg)

    def get_one_by_field(
        self: "CRUDBase[ModelType]",
        db: Session,
        field: str,
        value: str,
        case_insensitive: bool = False,  # noqa: FBT001, FBT002
    ) -> ModelType:
        """Returns an object of the model specified.

        Args:
            db (Session): Database session.
            field (str): Field of the row in the DB.
            value (str): Value to compare the Field with.
            case_insensitive (bool): If True, string comparisons ignore letter
                case. Defaults to False.

        Returns:
            ModelType: Element.

        Raises:
            ElementNotFoundError: If the element is not found.
        """
        logger.info("Entering...")
        logger.debug("Getting %s with %s: %s", self.model.__name__, field, value)
        filter_field = getattr(self.model, field)
        query_value = value
        if case_insensitive and isinstance(value, str):
            filter_field = func.lower(filter_field)
            query_value = value.lower()
        if data := db.query(self.model).filter(filter_field == query_value).first():
            logger.debug("Found %s with %s: %s", self.model.__name__, field, value)
            logger.info("Exiting...")
            return data
        error_msg = f"{self.model.__name__} with {field}: {value} not found."
        logger.error(error_msg)
        logger.info("Exiting...")
        raise ElementNotFoundError(error_msg)

    def get_one_by_fields(
        self: "CRUDBase[ModelType]",
        db: Session,
        filters: list[Filter],
        case_insensitive: bool = False,  # noqa: FBT001, FBT002
    ) -> ModelType:
        """Returns an object of the model specified.

        Args:
            db (Session): Database session.
            filters (dict[str, Tuple[str, object]]): Filters to apply, where each filter
                is a tuple of (operator, value).
            case_insensitive (bool): If True, string comparisons ignore letter
                case. Defaults to False.

        Returns:
            ModelType: Element.

        Raises:
            ElementNotFoundError: If the element is not found.
        """
        logger.info("Entering...")
        logger.debug("Getting %s with filters: %s", self.model.__name__, filters)
        filter_clauses = self._get_filters(filters, case_insensitive)
        if data := db.query(self.model).filter(*filter_clauses).first():
            logger.debug("Found %s with filters: %s", self.model.__name__, filters)
            logger.info("Exiting...")
            return data
        error_msg = f"{self.model.__name__} with filters: {filters} not found."
        logger.error(error_msg)
        logger.info("Exiting...")
        raise ElementNotFoundError(error_msg)

    def get_list(
        self: "CRUDBase[ModelType]",
        db: Session,
        offset: int | None = None,
        limit: int | None = None,
        filters: list[Filter] | None = None,
        filter_is_logic_and: bool = True,  # noqa: FBT001, FBT002
        order_by: str = "id",
        order_direction: Literal["asc", "desc"] = "asc",
        join_fields: list[str] | None = None,
        case_insensitive: bool = False,  # noqa: FBT001, FBT002
    ) -> Sequence[ModelType | None]:
        """Get a list of elements that can be filtered.

        Result requires mapping the objects to the desired response.

        Args:
            db (Session): Database session.
            offset (int | None = None): Omit a specified number of rows before
                the beginning of the result set. Defaults to None.
            limit (int | None = None): Limit the number of rows returned from a query.
                Defaults to None.
            filters (dict[str, Tuple[str, object]], optional): Filters to apply, where each filter
                is a tuple of (operator, value). Defaults to None.
            filter_is_logic_and (bool, optional): If True, the filters are applied with AND logic,
                otherwise with OR logic. Defaults to True.
            order_by (str, optional): Field to order the results by. Defaults to "id".
            order_direction (Literal["asc", "desc"], optional): Order direction for the results.
            join_fields (list[str], optional): List of foreign key fields to perform
                joined loading on. Defaults to None.
            case_insensitive (bool): If True, string comparisons ignore letter
                case. Defaults to False.

        Returns:
            list[ModelType | None]: Result with the Data.
        """
        logger.info("Entering...")
        logger.debug("Getting list of %s", self.model.__name__)
        query = select(self.model)
        if join_fields:
            for join_field in join_fields:
                query = query.join(getattr(self.model, join_field))

        if filters:
            filter_clauses = self._get_filters(filters, case_insensitive)
            if filter_is_logic_and:
                query = query.where(*filter_clauses)
            else:
                query = query.filter(or_(*filter_clauses))
            logger.debug("Filters applied: %s", filters)

        # Order by ID to ensure consistent ordering
        if order_direction == "desc":
            query = query.order_by(getattr(self.model, order_by).desc())
        else:
            query = query.order_by(getattr(self.model, order_by))
        logger.debug("Order by: %s", order_by)

        # Apply offset and limit - Pagination
        if offset:
            query = query.offset(offset)
            logger.debug("Offset: %s", offset)
        if limit:
            query = query.limit(limit)
            logger.debug("Limit: %s", limit)

        string_query = str(query)
        logger.debug("Query: %s", string_query)
        if data := db.scalars(query).all():
            logger.debug("Found list of %s", self.model.__name__)
            logger.info("Exiting...")
            return data
        logger.error("List of %s not found", self.model.__name__)
        logger.info("Exiting...")
        return []

    def count(
        self: "CRUDBase[ModelType]",
        db: Session,
        filters: list[Filter] | None = None,
    ) -> int:
        """Get the number of elements that can be filtered.

        Args:
            db (Session): Database session.
            filters (list[Filter], optional): Filters to apply, where each filter is a tuple
                of (operator, value). Defaults to None.

        Returns:
            int: Number of elements that match the query.
        """
        logger.info("Entering...")
        logger.debug("Counting %s", self.model.__name__)
        # Count distinct row ids instead of joined rows: filters that cross
        # relationships need an explicit join, otherwise the WHERE clause would
        # cross-join silently and inflate the total.
        ids_query = select(self.model.id)
        if filters:
            joined_relationships: set[str] = set()
            filter_clauses = []
            for filter_obj in filters:
                relationship_name, filter_field = self._resolve_field(filter_obj.field)
                if relationship_name and relationship_name not in joined_relationships:
                    ids_query = ids_query.join(getattr(self.model, relationship_name))
                    joined_relationships.add(relationship_name)
                filter_clauses.append(
                    self._get_filter_expression(filter_field, filter_obj.operator, filter_obj.value)
                )
            ids_query = ids_query.where(*filter_clauses)
            logger.debug("Filters applied: %s", filters)
        count_query = select(func.count()).select_from(ids_query.subquery())
        if data := db.scalar(count_query):
            logger.debug("Counted %s: %s", self.model.__name__, data)
            logger.info("Exiting...")
            return data
        logger.error("Count of %s not found", self.model.__name__)
        logger.info("Exiting...")
        return 0

    def get_unique_values(
        self: "CRUDBase[ModelType]",
        db: Session,
        column_name: str,
        include_nulls: bool = False,  # noqa: FBT001, FBT002
    ) -> list[Any]:
        """Get the unique values of a column, optionally excluding NULLs and empty strings.

        Args:
            db (Session): Database session.
            column_name (str): Name of the column to retrieve unique values from.
            include_nulls (bool): If False, excludes NULL values and, for string
                columns, empty strings. Defaults to False.

        Returns:
            list[Any]: Unique values of the specified column. Empty list when no rows match.

        Raises:
            AttributeError: If the column does not exist in the model.
            OperationalError: If an error occurs during the database operation.
        """
        logger.info("Entering...")
        logger.debug(
            "Retrieving unique values from column '%s' in %s",
            column_name,
            self.model.__name__,
        )
        if not hasattr(self.model, column_name):
            error_message = f"Column '{column_name}' does not exist in {self.model.__name__}."
            logger.error(error_message)
            raise AttributeError(error_message)

        try:
            _, column = self._resolve_field(column_name)
            query = select(column).distinct()
            # Excluding '' only makes sense for text columns; comparing other types
            # against an empty string would fail at the database level.
            if not include_nulls:
                query = query.where(column.isnot(None))
                if isinstance(column.type, String):
                    query = query.where(column != "")
            unique_values = list(db.scalars(query).all())
            logger.debug("Unique values found: %s", unique_values)
        except OperationalError:
            db.rollback()
            logger.exception(
                "Failed to retrieve unique values from column '%s' in %s",
                column_name,
                self.model.__name__,
            )
            raise
        else:
            return unique_values
        finally:
            logger.info("Exiting...")

    def create(self: "CRUDBase[ModelType]", db: Session, data: ModelType) -> ModelType:
        """Creates a new record in the database.

        Args:
            db (Session): The database session.
            data (ModelType): The data to be created.

        Returns:
            ModelType: The created data.
        """
        logger.info("Entering...")
        logger.debug("Creating %s object %s", self.model.__name__, data)
        try:
            db.add(data)
            db.commit()
            db.refresh(data)
            logger.debug("Created %s object %s", self.model.__name__, data)
        except OperationalError:
            db.rollback()
            logger.exception("Failed to create %s object %s", self.model.__name__, data)
            raise
        else:
            return data
        finally:
            logger.info("Exiting...")

    def bulk_create(
        self: "CRUDBase[ModelType]",
        db: Session,
        data: Sequence[ModelType],
    ) -> Sequence[ModelType]:
        """Creates multiple records in a single transaction.

        Args:
            db (Session): The database session.
            data (Sequence[ModelType]): The records to be created.

        Returns:
            Sequence[ModelType]: The created records, with their generated fields populated.

        Raises:
            OperationalError: If an error occurs during the operation.
        """
        logger.info("Entering...")
        logger.debug("Creating %s %s objects", len(data), self.model.__name__)
        try:
            db.add_all(data)
            db.commit()
            for record in data:
                db.refresh(record)
            logger.debug("Created %s %s objects", len(data), self.model.__name__)
        except OperationalError:
            db.rollback()
            logger.exception("Failed to create %s objects in bulk", self.model.__name__)
            raise
        else:
            return data
        finally:
            logger.info("Exiting...")

    def bulk_update(
        self: "CRUDBase[ModelType]",
        db: Session,
        data: Sequence[ModelType],
    ) -> Sequence[ModelType]:
        """Updates multiple existing records in a single transaction.

        Each record is merged by its primary key, so instances must already
        exist in the database.

        Args:
            db (Session): The database session.
            data (Sequence[ModelType]): The records to be updated.

        Returns:
            Sequence[ModelType]: The updated records.

        Raises:
            OperationalError: If an error occurs during the operation.
        """
        logger.info("Entering...")
        logger.debug("Updating %s %s objects", len(data), self.model.__name__)
        try:
            for record in data:
                db.merge(record)
            db.commit()
            for record in data:
                db.refresh(record)
            logger.debug("Updated %s %s objects", len(data), self.model.__name__)
        except OperationalError:
            db.rollback()
            logger.exception("Failed to update %s objects in bulk", self.model.__name__)
            raise
        else:
            return data
        finally:
            logger.info("Exiting...")

    def update(
        self: "CRUDBase[ModelType]",
        db: Session,
        data: ModelType,
    ) -> ModelType:
        """Update an existing record in the database.

        This method merges the provided data with the existing record in the database.
        If the operation is successful, the updated record is returned.
        If an OperationalError occurs during the operation, the changes are rolled back.

        Args:
            db (Session): The database session.
            data (ModelType): The data to be updated.

        Returns:
            ModelType: The updated record.

        Raises:
            OperationalError: If an error occurs during the operation.
        """
        logger.info("Entering...")
        logger.debug("Updating %s with object %s", self.model.__name__, data)
        try:
            db.merge(data)
            db.commit()
            db.refresh(data)
            logger.debug("Updated %s with object %s", self.model.__name__, data)
        except OperationalError:
            db.rollback()
            logger.exception("Failed to update %s object %s", self.model.__name__, data)
            raise
        else:
            return data
        finally:
            logger.info("Exiting...")

    def delete_row(
        self: "CRUDBase[ModelType]",
        db: Session,
        model_obj: ModelType,
    ) -> ModelType:
        """Delete a record from the database.

        This method retrieves the record and deletes it from the database.
        If the operation is successful, the deleted record is returned.
        If an OperationalError occurs during the operation, the changes are rolled back.

        Args:
            db (Session): The database session.
            model_obj (ModelType): The object of the record to be deleted.

        Returns:
            ModelType: The deleted record.

        Raises:
            OperationalError: If an error occurs during the operation.
        """
        logger.info("Entering...")
        logger.debug("Deleting %s object %s", self.model.__name__, model_obj)
        try:
            db.delete(model_obj)
            db.commit()
            logger.debug("Deleted %s object %s", self.model.__name__, model_obj)
        except OperationalError:
            db.rollback()
            logger.exception("Failed to delete %s object %s", self.model.__name__, model_obj)
            raise
        else:
            return model_obj
        finally:
            logger.info("Exiting...")

    def soft_delete_row(
        self: "CRUDBase[ModelType]",
        db: Session,
        model_obj: ModelType,
    ) -> ModelType:
        """Soft delete a record from the database.

        This method retrieves the record and sets its 'deleted_on' attribute to the
        current time.
        If the operation is successful, the updated record is returned.
        If an OperationalError occurs during the operation, the changes are rolled back.
        If the model does not support soft delete, a ValueError is raised.

        Args:
            db (Session): The database session.
            model_obj (ModelTypedelType): The object of the record to be soft deleted.

        Returns:
            ModelType: The updated record if found and soft deleted.

        Raises:
            OperationalError: If an error occurs during the operation.
            ValueError: If the model does not support soft delete.
        """
        logger.info("Entering...")
        logger.debug("Soft deleting %s object %s", self.model.__name__, model_obj)
        try:
            if not hasattr(model_obj, "deleted_on") or not hasattr(model_obj, "soft_delete"):
                logger.error("Model does not support soft delete.")
                error_message = "Model does not support soft delete."
                raise ValueError(error_message)
            logger.debug("Soft deleting %s by updating its values", self.model.__name__)
            return self.update(db, model_obj.soft_delete())
        except OperationalError:
            db.rollback()
            logger.exception("Failed to soft delete %sobject %s", self.model.__name__, model_obj)
            raise
        finally:
            logger.info("Exiting...")
