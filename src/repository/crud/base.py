"""CRUD object with default methods to Create, Read, Update, Delete (CRUD)."""

import logging
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar
from uuid import UUID

from pydantic import UUID4, BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Query as SQLQuery
from sqlalchemy.orm import Session

from src.repository.exceptions import ElementNotFoundError
from src.repository.models.base import Base

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from collections.abc import Callable

ModelType = TypeVar("ModelType", bound=Base)  # pylint: disable=invalid-name


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

    def _get_filter_expression(self, filter_field: Any, operator: str, value: any) -> SQLQuery:  # noqa: ANN401
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
    ) -> ModelType:
        """Returns an object of the model specified.

        Args:
            db (Session): Database session.
            field (str): Field of the row in the DB.
            value (str): Value to compare the Field with.

        Returns:
            ModelType: Element.

        Raises:
            ElementNotFoundError: If the element is not found.
        """
        logger.info("Entering...")
        logger.debug("Getting %s with %s: %s", self.model.__name__, field, value)
        if data := db.query(self.model).filter(getattr(self.model, field) == value).first():
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
    ) -> ModelType:
        """Returns an object of the model specified.

        Args:
            db (Session): Database session.
            filters (dict[str, Tuple[str, object]]): Filters to apply, where each filter
                is a tuple of (operator, value).

        Returns:
            ModelType: Element.

        Raises:
            ElementNotFoundError: If the element is not found.
        """
        logger.info("Entering...")
        logger.debug("Getting %s with filters: %s", self.model.__name__, filters)
        filter_clauses = self._get_filters(filters)
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
            filter_clauses = self._get_filters(filters)
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
        count_query = select(func.count()).select_from(self.model)  # pylint: disable=not-callable
        if filters:
            filter_clauses = self._get_filters(filters)
            count_query = count_query.where(*filter_clauses)
            logger.debug("Filters applied: %s", filters)
        if data := db.scalar(count_query):
            logger.debug("Counted %s: %s", self.model.__name__, data)
            logger.info("Exiting...")
            return data
        logger.error("Count of %s not found", self.model.__name__)
        logger.info("Exiting...")
        return 0

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
