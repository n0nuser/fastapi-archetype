from typing import Union

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Query as SQLQuery
from sqlalchemy.orm import joinedload

from src.db.models import Base, BaseDeletedOn
from src.db.session import Session


class Filter(BaseModel):
    """Filter to be applied to a query."""

    field: str
    operator: str
    value: str | int


def get_filters(db_model, items: list[Filter]) -> list[SQLQuery]:
    """Get the filters to be applied to a query.

    Args:
        db_model (_type_): SQLAlchemy Model to be queried.
        items (list[Filter]): List of filters to be applied.

    Raises:
        ValueError: If the operator is not supported.

    Returns:
        list[SQLQuery]: List of filters to be applied.
    """
    filter_clauses = []
    for filter_obj in items:
        filter_field = getattr(db_model, filter_obj.field)

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


def get_list(
    db_model: Base,
    limit: int,
    offset: int,
    filters: list[Filter] | None = None,
    default_query: SQLQuery | None = None,
    join_fields: list[str] | None = None,
) -> list[Base] | None:
    """Get a list of elements that can be filtered.
    Result requires mapping the objects to the desired response.

    Args:
        db_model (Base): Model to be queried for.
        limit (int): Limit the number of rows returned from a query.
        offset (int): Omit a specified number of rows before the beginning of the result set.
        filters (dict[str, Tuple[str, object]], optional): Filters to apply, where each filter is a tuple of (operator, value). Defaults to None.
        default_query (str, optional): Starting query before filtering and applying limits and offsets. Defaults to None.
        join_fields (list[str], optional): List of foreign key fields to perform joined loading on. Defaults to None.

    Returns:
        Union[list[Base], None]: Result with the Data or None if not found.
    """
    with Session() as session:
        default_query: SQLQuery = default_query or session.query(db_model)
        if join_fields:
            for join_field in join_fields:
                default_query: SQLQuery = default_query.options(
                    joinedload(getattr(db_model, join_field)),
                )

        if filters:
            filter_clauses = get_filters(db_model, filters)
            # OR
            # default_query = default_query.filter(sqlalchemy.or_(*filter_clauses))
            # AND
            default_query: SQLQuery = default_query.filter(*filter_clauses)

        db_elements = default_query.order_by(db_model.id.asc()).offset(offset).limit(limit).all()  # type: ignore
        return db_elements or None


def count(
    db_model: Base,
    filters: dict[str, tuple[str, object]] = None,  # type: ignore
) -> int:
    """Get the number of elements that can be filtered.

    Args:
        db_model (Base): Model to be queried for.
        filters (dict[str, Tuple[str, object]], optional): Filters to apply, where each filter is a tuple of (operator, value). Defaults to None.

    Returns:
        int: Number of elements that match the query.
    """
    with Session() as session:
        # default_query: SQLQuery = session.query(db_model)
        count_query = select(func.count()).select_from(db_model)
        if filters:
            filter_clauses = get_filters(db_model, filters)
            # OR
            # default_query = default_query.filter(sqlalchemy.or_(*filter_clauses))
            # AND
            count_query: SQLQuery = count_query.where(*filter_clauses)

        return session.scalar(count_query)


def get_by_id(
    db_model: Base,
    api_model_id: int,
    default_query: Query = None,  # type: ignore
    join_fields: list[str] = None,  # type: ignore
) -> Union[Base, None]:
    """Returns an object of the model specified.

    Args:
        db_model (Base): Model to be queried.
        api_model_id (int): ID of the row in the DB.
        default_query (Query, optional): Default query to be used. Defaults to None.
        join_fields (list[str], optional): List of foreign key fields to perform joined loading on. Defaults to None.

    Returns:
        Union[Base, None]: Element, or None if it wasn't found.
    """
    with Session() as session:
        default_query = default_query or session.query(db_model)
        if join_fields:
            for join_field in join_fields:
                default_query = default_query.options(joinedload(getattr(db_model, join_field)))
        return default_query.get(api_model_id)


def get_one_by_field(db_model: Base, field: str, value: str) -> Union[Base, None]:
    """Returns an object of the model specified.

    Args:
        db_model (Base): Model to be queried.
        field (str): Field of the row in the DB.
        value (str): Value to compare the Field with.

    Raises:
        sqlalchemy.orm.exc.NoResultFound: if the query selects no rows.
        sqlalchemy.orm.exc.MultipleResultsFound: if multiple object identities are returned, or if multiple rows are returned for a query that returns only scalar values as opposed to full identity-mapped entities.

    Returns:
        Base: Element of the DB.
    """
    with Session() as session:
        return session.query(db_model).filter(getattr(db_model, field) == value).one()


def delete_by_id(db_model: Base, api_model_id: int, soft_delete: bool = False) -> Union[Base, None]:
    """Deletes a Model instance by its ID.

    Args:
        db_model (Base): Model to be queried.
        api_model_id (int): ID of the object to be removed.
        soft_delete (bool): If the element calls soft_delete method of the model. Defaults to False.

    Raises:
        OperationalError: If there was a database error.

    Returns:
        Union[Base, None]: The deleted object or None if couldn't find the object.
    """
    with Session() as session:
        try:
            element: BaseDeletedOn = session.get(db_model, api_model_id)
            if element is None:
                return None
            if soft_delete and hasattr(element, "soft_delete"):
                element.soft_delete()
            else:
                session.delete(element)
            session.commit()
            return element
        except OperationalError as error:
            session.rollback()
            raise error


def create(model_object: Base) -> int:
    """Create a Model instance.

    Args:
        model_object (Base): DB Model instance to be created.

    Raises:
        OperationalError: If there was a database error.

    Returns:
        int: The ID of the created object.
    """
    with Session() as session:
        try:
            session.add(model_object)
            session.commit()
            return model_object.id
        except OperationalError as error:
            session.rollback()
            raise error


def update(model_object: Base) -> Union[Base, None]:
    """Updates the provided model object with the given object and returns the updated object.

    Args:
        model_object (Base): The model object that is going to be merge with the database.

    Raises:
        OperationalError: An exception that occurred during the database update.

    Returns:
        Base: The updated model object.
    """
    with Session() as session:
        try:
            session.merge(model_object)
            session.commit()
            return model_object
        except OperationalError as error:
            session.rollback()
            raise error
