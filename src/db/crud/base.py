from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Query as SQLQuery
from sqlalchemy.orm import Session, joinedload

from src.db.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class Filter(BaseModel):
    """Filter to be applied to a query."""

    field: str
    operator: str
    value: str | int


class CRUDBase(Generic[ModelType]):
    """CRUD object with default methods to Create, Read, Update, Delete (CRUD)."""

    def __init__(self: "CRUDBase", model: type[ModelType]) -> None:
        """CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def _get_filters(self: "CRUDBase", items: list[Filter]) -> list[SQLQuery]:
        """Get the filters to be applied to a query.

        Args:
            items (list[Filter]): List of filters to be applied.

        Raises:
            ValueError: If the operator is not supported.

        Returns:
            list[SQLQuery]: List of filters to be applied.
        """
        filter_clauses = []
        for filter_obj in items:
            filter_field = getattr(self.model, filter_obj.field)

            if filter_obj.operator == "eq":
                filter_clauses.append(filter_field == filter_obj.value)
            elif filter_obj.operator == "neq":
                filter_clauses.append(filter_field != filter_obj.value)
            elif filter_obj.operator == "contains":
                filter_clauses.append(filter_field.contains(filter_obj.value))
            elif filter_obj.operator == "not_contains":
                filter_clauses.append(~filter_field.contains(filter_obj.value))
            elif filter_obj.operator == "gt":
                filter_clauses.append(filter_field > filter_obj.value)
            elif filter_obj.operator == "gte":
                filter_clauses.append(filter_field >= filter_obj.value)
            elif filter_obj.operator == "lt":
                filter_clauses.append(filter_field < filter_obj.value)
            elif filter_obj.operator == "lte":
                filter_clauses.append(filter_field <= filter_obj.value)
            else:
                error_message = f"Operator {filter_obj.operator} not supported."
                raise ValueError(error_message)
        return filter_clauses

    def get_by_id(self: "CRUDBase", db: Session, row_id: int) -> ModelType | None:
        """Returns an object of the model specified.

        Args:
            db (Session): Database session.
            row_id (int): ID of the row in the DB.

        Returns:
            ModelType | None: Element, or None if it wasn't found.
        """
        return db.query(self.model).filter(self.model.id == row_id).first()

    def get_one_by_field(self: "CRUDBase", db: Session, field: str, value: str) -> ModelType | None:
        """Returns an object of the model specified.

        Args:
            db (Session): Database session.
            field (str): Field of the row in the DB.
            value (str): Value to compare the Field with.

        Returns:
            ModelType | None: Element of the DB.
        """
        return db.query(self.model).filter(getattr(self.model, field) == value).first()

    def get_list(
        self: "CRUDBase",
        db: Session,
        offset: int = 0,
        limit: int = 20,
        filters: list[Filter] | None = None,
        join_fields: list[str] | None = None,
    ) -> list[ModelType]:
        """Get a list of elements that can be filtered.

        Result requires mapping the objects to the desired response.

        Args:
            db (Session): Database session.
            offset (int): Omit a specified number of rows before the beginning of the result set.
            limit (int): Limit the number of rows returned from a query.
            filters (dict[str, Tuple[str, object]], optional): Filters to apply, where each filter
                is a tuple of (operator, value). Defaults to None.
            join_fields (list[str], optional): List of foreign key fields to perform
                joined loading on. Defaults to None.

        Returns:
            list[ModelType] | None: Result with the Data or None if not found.
        """
        query: SQLQuery = db.query(self.model)
        if join_fields:
            for join_field in join_fields:
                query = query.options(
                    joinedload(getattr(self.model, join_field)),
                )

        if filters:
            filter_clauses = self._get_filters(filters)
            # OR
            # query = query.filter(sqlalchemy.or_(*filter_clauses))
            # AND
            query = query.filter(*filter_clauses)

        db_elements = query.order_by(self.model.id.asc()).offset(offset).limit(limit).all()
        return db_elements or None  # type: ignore

    def count(
        self: "CRUDBase",
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
        count_query = select(func.count()).select_from(self.model)
        if filters:
            filter_clauses = self._get_filters(filters)
            count_query = count_query.where(*filter_clauses)
        return db.scalar(count_query)

    def create(self: "CRUDBase", db: Session, data: ModelType) -> ModelType:
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
        self: "CRUDBase",
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

    def delete_by_id(
        self: "CRUDBase",
        db: Session,
        model_id: int,
    ) -> ModelType | None:
        """Delete a record from the database by its id.

        This method retrieves the record by its id and deletes it from the database.
        If the operation is successful, the deleted record is returned.
        If an OperationalError occurs during the operation, the changes are rolled back.

        Args:
            db (Session): The database session.
            model_id (int): The id of the record to be deleted.

        Returns:
            ModelType | None: The deleted record if found, None otherwise.

        Raises:
            OperationalError: If an error occurs during the operation.
        """
        try:
            obj = db.query(self.model).get(model_id)
            if obj is None:
                return None
            db.delete(obj)
            db.commit()
        except OperationalError:
            db.rollback()
            raise
        else:
            return obj

    def soft_delete_by_id(
        self: "CRUDBase",
        db: Session,
        model_id: int,
    ) -> ModelType | None:
        """Soft delete a record from the database by its id.

        This method retrieves the record by its id and sets its 'deleted_on' attribute to the
        current time.
        If the operation is successful, the updated record is returned.
        If an OperationalError occurs during the operation, the changes are rolled back.
        If the model does not support soft delete, a ValueError is raised.

        Args:
            db (Session): The database session.
            model_id (int): The id of the record to be soft deleted.

        Returns:
            ModelType | None: The updated record if found and soft deleted, None otherwise.

        Raises:
            OperationalError: If an error occurs during the operation.
            ValueError: If the model does not support soft delete.
        """
        try:
            obj = db.query(self.model).get(model_id)
            if obj is None:
                return None
            if not hasattr(obj, "deleted_on"):
                error_message = "Model does not support soft delete."
                raise ValueError(error_message)
            return self.update(db, obj.soft_delete())
        except OperationalError:
            db.rollback()
            raise
