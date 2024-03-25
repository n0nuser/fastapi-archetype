from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar
from uuid import UUID

from pydantic import UUID4, BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Query as SQLQuery
from sqlalchemy.orm import Session

from src.core.logger import logger
from src.repository.exceptions import ElementNotFoundError
from src.repository.models.base import Base

if TYPE_CHECKING:
    from collections.abc import Callable

ModelType = TypeVar("ModelType", bound=Base)


class Filter(BaseModel):
    """Filter to be applied to a query."""

    field: str = Field(..., examples=["name"])
    operator: Literal["eq", "neq", "contains", "not_contains", "gt", "gte", "lt", "lte"] = Field(
        ...,
        examples=["eq"],
    )
    value: str | int | float | bool | UUID = Field(..., examples=["John Doe"])


class CRUDBase(Generic[ModelType]):
    """CRUD object with default methods to Create, Read, Update, Delete (CRUD)."""

    def __init__(self: "CRUDBase[ModelType]", model: type[ModelType]) -> None:
        """CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def _get_filter_expression(self, filter_field: Any, operator: str, value: any) -> SQLQuery:
        """
        Return the filter expression based on the operator and value.

        Args:
            filter_field: The SQLAlchemy model field to apply the filter on.
            operator: The filter operation to perform (e.g., "eq", "neq").
            value: The value to compare the field against.

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

        return operators[operator](filter_field)

    def _get_filters(self, items: list["Filter"]) -> list[SQLQuery]:
        """
        Get the filters to be applied to a query.

        Args:
            items: A list of Filter objects specifying the filters to apply.

        Returns:
            A list of SQLAlchemy query objects representing the filters to be applied.
        """
        filter_clauses = []
        for filter_obj in items:
            field_parts = filter_obj.field.split(".")
            filter_field = getattr(self.model, field_parts[0])

            for part in field_parts[1:]:
                filter_field = getattr(filter_field.property.mapper.class_, part)

            filter_clauses.append(
                self._get_filter_expression(filter_field, filter_obj.operator, filter_obj.value)
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
            : If the element is not found.
        """
        if data := db.query(self.model).filter(self.model.id == row_id).first():
            return data
        raise ElementNotFoundError

    def get_one_by_field(
        self: "CRUDBase[ModelType]",
        db: Session,
        field: str,
        value: str,
    ) -> ModelType:
        """Returns an object of the model specified.

        Args:
            db (Session): Database session.
            field (str): Field of the row in the DB.
            value (str): Value to compare the Field with.

        Returns:
            ModelType: Element.

        Raises:
            : If the element is not found.
        """
        if data := db.query(self.model).filter(getattr(self.model, field) == value).first():
            return data
        raise ElementNotFoundError

    def get_one_by_fields(
        self: "CRUDBase[ModelType]",
        db: Session,
        filters: list[Filter],
    ) -> ModelType:
        """Returns an object of the model specified.

        Args:
            db (Session): Database session.
            filters (dict[str, Tuple[str, object]]): Filters to apply, where each filter
                is a tuple of (operator, value).

        Returns:
            ModelType: Element.

        Raises:
            : If the element is not found.
        """
        filter_clauses = self._get_filters(filters)
        if data := db.query(self.model).filter(*filter_clauses).first():
            return data
        raise ElementNotFoundError

    def get_list(
        self: "CRUDBase[ModelType]",
        db: Session,
        offset: int | None = None,
        limit: int | None = None,
        filters: list[Filter] | None = None,
        join_fields: list[str] | None = None,
    ) -> list[ModelType]:
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
            join_fields (list[str], optional): List of foreign key fields to perform
                joined loading on. Defaults to None.

        Returns:
            list[ModelType]: Result with the Data.

        Raises:
            ElementNotFoundError: If the element is not found.
        """
        query = select(self.model)
        if join_fields:
            for join_field in join_fields:
                query = query.join(getattr(self.model, join_field))

        if filters:
            filter_clauses = self._get_filters(filters)
            # OR
            # query = query.filter(sqlalchemy.or_(*filter_clauses))
            # AND
            query = query.where(*filter_clauses)

        # Order by ID to ensure consistent ordering
        query = query.order_by(self.model.id)

        # Apply offset and limit - Pagination
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        string_query = str(query)
        logger.debug(string_query)
        if data := db.scalars(query).all():
            return data
        raise ElementNotFoundError

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

        Raises:
            : If the element is not found.
        """
        count_query = select(func.count()).select_from(self.model)
        if filters:
            filter_clauses = self._get_filters(filters)
            count_query = count_query.where(*filter_clauses)
        if data := db.scalar(count_query):
            return data  # type: ignore
        raise ElementNotFoundError

    def create(self: "CRUDBase[ModelType]", db: Session, data: ModelType) -> ModelType:
        """Creates a new record in the database.

        Args:
            db (Session): The database session.
            data (ModelType): The data to be created.

        Returns:
            ModelType: The created data.
        """
        try:
            db.add(data)
            db.commit()
            db.refresh(data)
        except OperationalError:
            db.rollback()
            raise
        else:
            return data

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
        try:
            db.merge(data)
            db.commit()
            db.refresh(data)
        except OperationalError:
            db.rollback()
            raise
        else:
            return data

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
        try:
            db.delete(model_obj)
            db.commit()
        except OperationalError:
            db.rollback()
            raise
        else:
            return model_obj

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
        try:
            if not hasattr(model_obj, "deleted_on") or not hasattr(model_obj, "soft_delete"):
                error_message = "Model does not support soft delete."
                raise ValueError(error_message)
            return self.update(db, model_obj.soft_delete())
        except OperationalError:
            db.rollback()
            raise
