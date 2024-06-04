"""Module with base schemas for the API."""

from typing import Any

from fastapi import Query


def DashingQuery(  # noqa: N802
    default: Any,  # noqa: ANN401
    *,
    convert_underscores: bool = True,
    **kwargs: dict[str, Any],
) -> Any:  # noqa: ANN401
    """Create a query parameter with dashes.

    Args:
        default (Any): The default value of the query parameter.
        convert_underscores (bool, optional): Convert Underscores to Dashes. Defaults to True.
        kwargs (dict[str, Any]): Additional keyword arguments for the query parameter.

    Returns:
        Any: The query parameter.
    """
    query = Query(default, **kwargs)
    query.convert_underscores = convert_underscores
    return query
