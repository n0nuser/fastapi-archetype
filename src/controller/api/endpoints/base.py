"""Common query parameters."""

from typing import Annotated, Any

from fastapi import Header
from pydantic import UUID4


async def common_query_parameters(
    x_request_id: Annotated[UUID4, Header(description="Request ID.")],
    accept_language: Annotated[
        str | None,
        Header(
            ...,
            description="ISO code of the language that the"  # noqa: ISC003
            + " client accepts in response from the server.",
            regex=r"(\*)|(^[a-z]+(-[A-Z])*(,[a-z]*;(q=[0-9].[0.9])*)*)",
            min_length=1,
        ),
    ] = None,
) -> dict[str, Any]:
    """Common query parameters.

    Args:
        x_request_id (Annotated[UUID4, Header, optional): Request ID)].
        accept_language (_type_, optional): ISO code of the language that the
            client accepts in response from the server.

    Returns:
        dict[str, Any]: A dictionary with the common query parameters.
    """
    return {"x_request_id": x_request_id, "accept_language": accept_language}
