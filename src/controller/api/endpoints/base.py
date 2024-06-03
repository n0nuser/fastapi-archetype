"""Common query parameters."""

from typing import Annotated, Any

from fastapi import Header


async def common_query_parameters(
    accept_language: Annotated[
        str,
        Header(
            ...,
            description="ISO code of the language that the"  # noqa: ISC003
            + " client accepts in response from the server.",
            regex=r"(\*)|(^[a-z]+(-[A-Z])*(,[a-z]*;(q=[0-9].[0.9])*)*)",
            min_length=1,
        ),
    ] = "en-US",
) -> dict[str, Any]:
    """Common query parameters.

    Args:
        accept_language (_type_, optional): ISO code of the language that the
            client accepts in response from the server.

    Returns:
        dict[str, Any]: A dictionary with the common query parameters.
    """
    return {"accept-language": accept_language}
